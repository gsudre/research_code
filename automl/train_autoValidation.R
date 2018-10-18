# gets dummy values using similar data split as in autoValidation. Note that
# here we're using caret to keep the training labels with the correct
# probabilities in train and test sets, so there's no need to do it multiple
# times, as everything comes from the trainin set anyways.

args <- commandArgs(trailingOnly = TRUE)
data_fname = args[1]
clin_fname = args[2]
target = args[3]

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
# for pairwise, we can do the usual nvVSper, nvVSrem, perVSrem, then
# groupOLS_SX_slope_ plus nvVSimp, nvVSnonimp, impVSnonimp, plus all of them
# using nonew_
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
# pairwise comparisons
if (grepl('VS', target)) {
    df[, 'groupSlope'] = 'nonimprovers'
    if (grepl('groupOLS', target)) {
        tmp = strsplit(target, '_')[[1]]
        slope_name = paste(tmp[1:(length(tmp)-1)], collapse='_')
        slope_name = sub('group', '', slope_name)
        df[df[, slope_name] < 0, 'groupSlope'] = 'improvers'
        if (grepl('nv', target)) {
            df[df$diag_group2 == 1, 'groupSlope'] = 'nv'
        }
        df$groupSlope = as.factor(df$groupSlope)
        target = tmp[length(tmp)]  # get the VS part only
    }
    groups = strsplit(target, 'VS')
    group1 = groups[[1]][1]
    group2 = groups[[1]][2]
    keep_me = F
    if (group1 == 'nv' || group2 == 'nv') {
        keep_me = keep_me | df$diag_group2 == 1
    }
    if (group1 == 'per' || group2 == 'per') {
        keep_me = keep_me | df$diag_group2 == 3
        target = 'diag_group2'
    }
    if (group1 == 'rem' || group2 == 'rem') {
        keep_me = keep_me | df$diag_group2 == 2
        target = 'diag_group2'
    }
    if (group1 == 'imp' || group2 == 'imp') {
        keep_me = keep_me | df$groupSlope == 'improvers'
        target = 'groupSlope'
    }
    if (group1 == 'nonimp' || group2 == 'nonimp') {
        keep_me = keep_me | df$groupSlope == 'nonimprovers'
        target = 'groupSlope'
    }
    # remove NVs if we are doing imp vs nonImp
    if (sum(keep_me) == nrow(df)) {
        df = df[df$diag_group2 != 1, ]
    } else {
        df = df[keep_me, ]
    }
    df[, target] = as.factor(as.character(df[, target]))
}

# set seed again to replicate old results
library(caret)
train_idx = sort(createDataPartition(df[, target], p = .9, list = FALSE, times = 1))
test_idx = sort(setdiff(1:nrow(df), train_idx)) # H2o only deals with sorted indexes
data.test = df[test_idx, ]
data.train = df[train_idx, ]
print(sprintf('Using %d samples for training + validation, %d for testing.',
              nrow(data.train),
              nrow(data.test)))

# dummy classifier
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
# just to have an idea of which one is the negative class (level 0)
print(levels(data.train[, target]))