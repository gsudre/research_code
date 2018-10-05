# gets random values using similar data split as in autoValidation

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
train_idx = sort(idx[(mylim + 1):nrow(df)])
data.test = df[test_idx, ]
data.train = df[train_idx, ]
print(sprintf('Using %d samples for training + validation, %d for testing.',
              nrow(data.train),
              nrow(data.test)))

# dummy classifier
library(caret)
if (grepl(pattern = 'group', target)) {
    df[,target] = as.factor(df[,target])
    data.test[,target] = factor(data.test[,target], levels=levels(df[,target]))
    probs = table(data.train[,target])/nrow(data.train)
    preds = as.data.frame(matrix(rep(probs, each=nrow(data.test)),
                                nrow=nrow(data.test)))
    colnames(preds) = names(probs)
    preds$obs = data.test[,target]
    preds$pred = names(probs)[probs==max(probs)]
    preds$pred = factor(preds$pred, levels=levels(df[,target]))
    print(multiClassSummary(preds, lev = levels(preds$obs)))
} else {
    preds = rep(mean(data.train[,target]), nrow(data.test))
    SSres = sum((data.test[, target] - preds)**2)
    SStot = sum((data.test[, target] - mean(data.train[, target]))**2)
    print(sprintf('Predicting mean R2: %.2f', 1-SSres/SStot))
    print(postResample(pred = preds, obs = data.test[, target]))

    preds = rep(median(data.train[,target]), nrow(data.test))
    SSres = sum((data.test[, target] - preds)**2)
    print(sprintf('Predicting median R2: %.2f', 1-SSres/SStot))
    print(postResample(pred = preds, obs = data.test[, target]))
}

print(data_fname)
print(clin_fname)
print(target)