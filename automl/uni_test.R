# runs classification tasks using AutoML from H2O

args <- commandArgs(trailingOnly = TRUE)
data_fname = args[1]
clin_fname = args[2]
target = args[3]
export_fname = args[4]
myseed = as.numeric(args[5])


winsorize = function(x, cut = 0.01){
  cut_point_top <- quantile(x, 1 - cut, na.rm = T)
  cut_point_bottom <- quantile(x, cut, na.rm = T)
  i = which(x >= cut_point_top) 
  x[i] = cut_point_top
  j = which(x <= cut_point_bottom) 
  x[j] = cut_point_bottom
  return(x)
}

# starting h2o
library(h2o)
if (Sys.info()['sysname'] == 'Darwin') {
  max_mem = '16G'
} else {
  max_mem = paste(Sys.getenv('SLURM_MEM_PER_NODE'),'m',sep='')
}
h2o.init(ip='localhost', nthreads=future::availableCores(),
         max_mem_size=max_mem,
         port=sample(50000:60000, 1))  # jobs on same node use different ports

print('Loading files')
# merging phenotype and clinical data
clin = read.csv(clin_fname)
load(data_fname)  #variable is data
# remove constant variables that screw up PCA and univariate tests
print('Removing constant variables')
feat_var = apply(data, 2, var, na.rm=TRUE)
idx = feat_var != 0  # TRUE for features with 0 variance (constant)
# categorical variables give NA variance, but we want to keep them
idx[is.na(idx)] = TRUE
data = data[, idx]
nNAs = colSums(is.na(data))  # number of NAs in each variable
# remove variables that are all NAs
data = data[, nNAs < nrow(data)]
print(sprintf('Features remaining: %d (%d with NAs)', ncol(data)-1, sum(nNAs>0)))
print('Merging files')
df = merge(clin, data, by='MRN')
print('Looking for data columns')
x = colnames(df)[grepl(pattern = '^v', colnames(df))]

# checking for subgroup analysis. Options are nonew_OLS_*_slope, nonew_diag_group2,
# ADHDonly_OLS_*_slope, ADHDonly_diag_group2, nonew_ADHDonly_*, ADHDNOS_OLS_*_slope,
# ADHDNOS_groupOLS_*_slope, nonew_ADHDNOS_*
if (grepl('nonew', target)) {
  df = df[df$diag_group != 'new_onset', ]
  df$diag_group = factor(df$diag_group)
  target = sub('nonew_', '', target)
}
if (grepl('ADHDonly', target)) {
  df = df[df$diag_group != 'unaffect', ]
  df$diag_group = factor(df$diag_group)
  target = sub('ADHDonly_', '', target)
}
if (grepl('ADHDNOS', target)) {
  df = df[df$DX != 'NV', ]
  target = sub('ADHDNOS_', '', target)
  if (grepl('groupOLS', target) || grepl('grouprandom', target)) {
    df[, target] = 'nonimprovers'
    slope = sub('group', '', target)
    df[df[, slope] < 0, target] = 'improvers'
    df[, target] = as.factor(df[, target])
  }
}

set.seed(myseed)
idx = sample(1:nrow(df), nrow(df), replace=F)
mylim = floor(.10 * nrow(df))
test_idx = sort(idx[1:mylim])  # H2o only deals with sorted indexes
valid_idx = sort(idx[(mylim + 1):(2 * mylim)])
train_idx = sort(idx[(2 * mylim + 1):nrow(df)])
data.test = df[test_idx, ]
data.valid = df[valid_idx, ]
data.train = df[train_idx, ]
print(sprintf('Using %d samples for training, %d for validation, %d for testing.',
              nrow(data.train),
              nrow(data.valid),
              nrow(data.test)))

print('Running univariate analysis')
# winsorize and get univariates if it's a continuous variable
if (! grepl(pattern = 'group', target)) {
    b = sapply(data.train[, x],
                function(myx) {
                res = cor.test(myx, data.train[, target], method='spearman');
                return(res$p.value)
                })
    # winsorizing after correlations to avoid ties
    data.train[, target] = winsorize(data.train[, target])
    cut_point_top = max(data.train[, target])
    cut_point_bottom = min(data.train[, target])
    i = which(data.test[, target] >= cut_point_top) 
    data.test[i, target] = cut_point_top
    j = which(data.test[, target] <= cut_point_bottom) 
    data.test[j, target] = cut_point_bottom
    i = which(data.valid[, target] >= cut_point_top) 
    data.valid[i, target] = cut_point_top
    j = which(data.valid[, target] <= cut_point_bottom) 
    data.valid[j, target] = cut_point_bottom
} else {
    data.train[, target] = as.factor(data.train[, target])
    b = sapply(data.train[,x],
                function(myx) {
                res = kruskal.test(myx, data.train[, target]);
                return(res$p.value)
                })
}
keep_me = b <= .05
x = x[keep_me]

print('Converting to H2O')
dtrain = as.h2o(data.train[, c(x, target)])
dtest = as.h2o(data.test[, c(x, target)])
dvalid = as.h2o(data.valid[, c(x, target)])
if (grepl(pattern = 'group', target)) {
    outcome = as.factor(as.h2o(df[, target]))  # making sure we have correct levels
    dtrain[, target] = outcome[train_idx]
    dtest[, target] = outcome[test_idx]
    dvalid[, target] = outcome[valid_idx]
}

print(sprintf('Running model on %d features', length(x)))
aml <- h2o.automl(x = x, y = target, training_frame = dtrain,
                seed=myseed,
                validation_frame=dvalid,
                leaderboard_frame=dtest,
                max_runtime_secs = NULL,
                max_models = NULL)

print(aml@leaderboard)
h2o.saveModel(aml@leader, path = export_fname)

# dummy classifier
if (grepl(pattern = 'group', target)) {
    print('Class distribution:')
    print(as.vector(h2o.table(dtrain[,target])['Count'])/nrow(dtrain))
} else {
    preds = rep(mean(dtrain[,target]), nrow(dtrain))
    m = h2o.make_metrics(as.h2o(preds), dtrain[, target])
    print('MSE prediction mean:')
    print(m@metrics$MSE)
}

print(data_fname)
print(clin_fname)
print(target)