# runs classification tasks using AutoML from H2O, uses leaderboard from CV. Not
# set-up for winsorization!

args <- commandArgs(trailingOnly = TRUE)
data_fname = args[1]
clin_fname = args[2]
target = args[3]
export_fname = args[4]
myseed = as.numeric(args[5])
dimres = args[6]


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
    if (group1 == 'adhd' || group2 == 'adhd') {
        df[df$diag_group2 == 3, 'diag_group2'] = 2
        keep_me = keep_me | df$diag_group2 == 2
        target = 'diag_group2'
    }
    # remove NVs if we are doing imp vs nonImp
    if (sum(keep_me) == nrow(df) && (grepl('imp', group1) || grepl('imp', group2))) {
        df = df[df$diag_group2 != 1, ]
    } else {
        df = df[keep_me, ]
    }
    df[, target] = as.factor(as.character(df[, target]))
    print(table(df[, target]))
}

# use negative seed to randomize the data
if (myseed < 0) {
  print('Creating random data!!!')
  myseed = -1 * myseed
  set.seed(myseed)
  rnd_data = matrix(runif(nrow(df)*length(x),
                          min(df[,x], na.rm=T), max(df[,x], na.rm=T)),
                    nrow(df), length(x))
  df[, x] = rnd_data
}

nfeats = min(nrow(df)-1, floor(sqrt(length(x))))  # variables to keep
if (dimres == 'PCA') {
    print(sprintf('Running %s', dimres))
    # quick hack to use na.action on prcomp
    fm_str = sprintf('~ %s', paste0(x, collapse='+ ', sep=' '))
    pca = prcomp(as.formula(fm_str), df[, x], scale=T, na.action=na.exclude)
    # eigs <- pca$sdev^2
    # vexp = cumsum(eigs)/sum(eigs)
    # keep_me = vexp <= .7
    keep_me = 1:nfeats
    a = cbind(pca$x[, keep_me], df[, target])
    colnames(a)[ncol(a)] = target
    x = colnames(a)[grepl(pattern = '^PC', colnames(a))]
    df = a
} else if (dimres == 'ICA') {
    print(sprintf('Running %s', dimres))
    library(fastICA)
    set.seed(myseed)
    ica = fastICA(df[, x], nfeats, method='C')
    a = cbind(as.data.frame(ica$S), df[, target])
    cnames = c(sapply(1:ncol(a), function(d) sprintf('IC%03d', d)))
    colnames(a) = cnames
    colnames(a)[ncol(a)] = target
    x = colnames(a)[grepl(pattern = '^IC', colnames(a))]
    df = a
} else if (dimres == 'PCA-elbow') {
    print(sprintf('Running %s', dimres))
    # quick hack to use na.action on prcomp
    fm_str = sprintf('~ %s', paste0(x, collapse='+ ', sep=' '))
    pca = prcomp(as.formula(fm_str), df[, x], scale=T, na.action=na.exclude)
    eigs <- pca$sdev^2
    library(nFactors)
    nS = nScree(x=eigs)
    print(nS)
    keep_me = 1:nS$Components$noc
    a = cbind(pca$x[, keep_me], df[, target])
    colnames(a)[ncol(a)] = target
    x = colnames(a)[grepl(pattern = '^PC', colnames(a))]
    df = a
} else if (dimres == 'PCA-kaiser') {
    print(sprintf('Running %s', dimres))
    # quick hack to use na.action on prcomp
    fm_str = sprintf('~ %s', paste0(x, collapse='+ ', sep=' '))
    pca = prcomp(as.formula(fm_str), df[, x], scale=T, na.action=na.exclude)
    eigs <- pca$sdev^2
    library(nFactors)
    nS = nScree(x=eigs)
    keep_me = 1:nS$Components$nkaiser
    a = cbind(pca$x[, keep_me], df[, target])
    colnames(a)[ncol(a)] = target
    x = colnames(a)[grepl(pattern = '^PC', colnames(a))]
    df = a
}

# set seed again to replicate old results
set.seed(myseed)
print(sprintf('Using all %d samples for training + validation (CV results for leaderboard).',
              nrow(df)))

print('Converting to H2O')
dtrain = as.h2o(df[, c(x, target)])
if (grepl(pattern = 'group', target)) {
    outcome = as.factor(as.h2o(df[, target]))  # making sure we have correct levels
    dtrain[, target] = outcome
}

# make sure the SNPs are seen as factors
if (grepl(pattern = 'snp', data_fname)) {
  print('Converting SNPs to categorical variables')
  for (v in x) {
    dtrain[, v] = as.factor(dtrain[, v])
  }
}

# make sure some of the socioeconomic variables are seen as factors
if (grepl(pattern = 'social', data_fname)) {
  print('Converting some socioeconomics to categorical variables')
  for (v in c('v_CategCounty', 'v_CategHomeType')) {
      if (v %in% x) {
          dtrain[, v] = as.factor(dtrain[, v])
      }
  }
}

# use all binary clinic variables, regardless of univariate results
if (grepl(pattern = 'clinic', data_fname)) {
  print('Converting binary clinical variables')
  x = colnames(df)[grepl(pattern = '^v', colnames(df))]
  xbin = colnames(df)[grepl(pattern = '^vCateg', colnames(df))]
  for (v in xbin) {
    dtrain[, v] = as.factor(dtrain[, v])
  }
}

# use all adhd200 variables, regardless of univariate results
if (grepl(pattern = 'adhd', data_fname)) {
  print('Converting categorical variables')
  x = colnames(df)[grepl(pattern = '^v', colnames(df))]
  xbin = colnames(df)[grepl(pattern = '^vCateg', colnames(df))]
  for (v in xbin) {
    dtrain[, v] = as.factor(dtrain[, v])
  }
}

if (dimres == 'AutoEncoder') {
    print(sprintf('Running %s', dimres))
    model=h2o.deeplearning(x=x, training_frame=dtrain,
                           hidden=c(3*nfeats, nfeats, 3*nfeats),
                           autoencoder=T, activation="Tanh", l1=1)
    features = h2o.deepfeatures(model, dtrain, layer=2)
    dtrain = h2o.cbind(features, dtrain[, target])
    colnames(dtrain)[ncol(dtrain)] = target
    x = colnames(features)
}

print(sprintf('Running model on %d features', length(x)))
aml <- h2o.automl(x = x, y = target, training_frame = dtrain,
                seed=myseed,
                max_runtime_secs = NULL,
                max_models = NULL,
                exclude_algos = c("StackedEnsemble"))

print(aml@leaderboard)

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

# print predictions
print('CV predictions:')
preds = h2o.getFrame(aml@leader@model[["cross_validation_holdout_predictions_frame_id"]][["name"]])
print(preds, n=nrow(preds))

# print all model metrics on CV data
print(aml@leader)

# last thing is saving model, in case there are any permissions or I/O errors
h2o.saveModel(aml@leader, path = export_fname)