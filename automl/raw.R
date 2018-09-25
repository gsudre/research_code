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
h2o.init(ip='localhost', nthreads=future::availableCores(), max_mem_size=max_mem)

print('Loading files')
# merging phenotype and clinical data
clin = read.csv(clin_fname)
load(data_fname)  #variable is data
# remove constant variables that screw up PCA and univariate tests
print('Removing constant variables and NAs')
keep_me = colSums(is.na(data)) == 0
data = data[, keep_me]
feat_var = apply(data, 2, var, na.rm=TRUE)
data = data[, feat_var != 0]
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
  if (grepl('group', target)) {
    df[, target] = 'nonimprovers'
    slope = sub('group', '', target)
    df[df[, slope] < 0, target] = 'improvers'
    df[, target] = as.factor(df[, target])
  }
}

set.seed(myseed)
idx = sample(1:nrow(df), nrow(df), replace=F)
mylim = floor(.10 * nrow(df))
data.test = df[idx[1:mylim], ]
data.train = df[idx[(mylim + 1):nrow(df)], ]
print(sprintf('Using %d samples for training, %d for validation.',
              nrow(data.train),
              nrow(data.test)))

# winsorize if continuous variable
if (! grepl(pattern = 'group', target)) {
  data.train[, target] = winsorize(data.train[, target])
  cut_point_top = max(data.train[, target])
  cut_point_bottom = min(data.train[, target])
  i = which(data.test[, target] >= cut_point_top) 
  data.test[i, target] = cut_point_top
  j = which(data.test[, target] <= cut_point_bottom) 
  data.test[j, target] = cut_point_bottom
}

print('Converting to H2O')
dtrain = as.h2o(data.train[, c(x, target)])
dtest = as.h2o(data.test[, c(x, target)])
if (grepl(pattern = 'group', target)) {
  dtrain[, target] = as.factor(dtrain[, target])
  dtest[, target] = as.factor(dtest[, target])
}

# make sure the SNPs are seen as factors
if (grepl(pattern = 'snp', data_fname)) {
  print('Converting SNPs to categorical variables')
  for (v in x) {
    dtrain[, v] = as.factor(dtrain[, v])
    dtest[, v] = as.factor(dtest[, v])
  }
}

print(sprintf('Running model on %d features', length(x)))
aml <- h2o.automl(x = x, y = target, training_frame = dtrain,
                  seed=myseed,
                  validation_frame=dtest,
                  max_runtime_secs = NULL,
                  max_models = NULL)

print(data_fname)
print(clin_fname)
print(target)
print(aml@leaderboard)
h2o.saveModel(aml@leader, path = export_fname)

# dummy classifier
if (grepl(pattern = 'group', target)) {
  print('Class distribution:')
  print(as.vector(h2o.table(df2[,target])['Count'])/nrow(df2))
} else {
  preds = rep(mean(df2[,target]), nrow(df2))
  m = h2o.make_metrics(as.h2o(preds), df2[, target])
  print('MSE prediction mean:')
  print(m@metrics$MSE)
}