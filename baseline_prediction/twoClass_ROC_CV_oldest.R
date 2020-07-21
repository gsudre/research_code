args <- commandArgs(trailingOnly = TRUE)

library(caret)
library(doParallel)

if (length(args) > 0) {
    fname = args[1]
    phen = args[2]
    c1 = args[3]
    c2 = args[4]
    clf_model = args[5]
    impute = args[6]
    nfolds = as.numeric(args[7])
    nreps = as.numeric(args[8])
    ncores = as.numeric(args[9])
    use_covs = as.logical(args[10])
    out_file = args[11]
} else {
    fname = '~/data/baseline_prediction/gf_JULY_ols_definition_GS.csv'
    phen = 'categ_all_lm'
    c1 = 'worsening'
    c2 = 'improvers'
    clf_model = 'slda'
    impute = 'dti'
    ncores = 2
    nfolds = 10
    nreps = 10
    use_covs = FALSE
    out_file = '/dev/null'
}

data = read.csv(fname)
data$sex_numeric = as.factor(data$sex_numeric)
data$SES_group3 = as.factor(data$SES_group3)
var_names = c(# PRS
              'ADHD_PRS0.000100.orig', 'ADHD_PRS0.001000.orig',
              'ADHD_PRS0.010000.orig', 'ADHD_PRS0.050000.orig',
              'ADHD_PRS0.100000.orig', 'ADHD_PRS0.200000.orig',
              'ADHD_PRS0.300000.orig', 'ADHD_PRS0.400000.orig',
              'ADHD_PRS0.500000.orig',
              # DTI
              'atr_fa', 'cst_fa', 'cing_cing_fa', 'cing_hipp_fa', 'cc_fa',
              'ilf_fa', 'slf_fa', 'unc_fa',
              # demo
              'sex_numeric', 'SES_group3',
              # cog
              'FSIQ', 'SS_RAW', 'DS_RAW', 'PS_RAW', 'VMI.beery_RAW',
              # anat
              'cerebellum_white', 'cerebellum_grey', 'amygdala',
              'cingulate', 'lateral_PFC', 'OFC', 'striatum', 'thalamus'
              )

covar_names = c(# DTI
                'norm.rot', 'norm.trans', # base_age, gender,
                # cog
                # base_age, gender
                # anat
                'average_qc', # age, gender (but not ICV)
                # PRS
                sapply(1:10, function(x) sprintf('PC%02d', x)) # age, gender
                # demo
                # just base_age (as gender one was of the targets)
                )

if (use_covs) {
    data2 = data[, c(var_names, covar_names)]
} else {
    data2 = data[, var_names]
}

if (impute == 'dti') {
    use_me = !is.na(data2$slf_fa)
    data2 = data2[use_me, ]
    print(sprintf('Using %d observations, %d predictors.', nrow(data2),
                  ncol(data2))) 
} else if (impute == 'anat') {
    use_me = !is.na(data2$thalamus)
    data2 = data2[use_me, ]
    dti_cols = which(grepl(colnames(data2), pattern='_fa$'))
    data2 = data2[, -dti_cols]
    if (use_covs) {
        dti_cols = which(grepl(colnames(data2), pattern='^norm'))
        data2 = data2[, -dti_cols]
    }
    print(sprintf('Using %d observations, %d predictors.', nrow(data2),
                  ncol(data2)))
} else {
    use_me = TRUE
    print('No imputation needed')
}

# will need this later so training rows match data2
data = data[use_me, ]
data2$phen = as.factor(data[, phen])

# selecting only kids in the 2 specified groups
keep_me = data2$phen==c1 | data2$phen==c2
data2 = data2[keep_me, ]
data = data[keep_me, ]

# split traing and test between members of the same family
train_rows = c()
for (fam in unique(data$FAMID)) {
    fam_rows = which(data$FAMID == fam)
    if (length(fam_rows) == 1) {
        train_rows = c(train_rows, fam_rows[1])
    } else {
        # choose the oldest kid in the family for training
        train_rows = c(train_rows,
                       fam_rows[which.max(data[fam_rows, 'base_age'])])
    }
}
X = data2[train_rows, -ncol(data2)]
y = factor(data2[train_rows,]$phen)

dummies = dummyVars(~ ., data = X, fullRank=T)
X = predict(dummies, newdata = X)

# imputation and feature engineering
set.seed(42)
pp_order = c('zv', 'nzv', 'corr', 'YeoJohnson', 'center', 'scale', 'bagImpute')

registerDoParallel(ncores)
getDoParWorkers()
set.seed(42)
fitControl <- trainControl(method = "repeatedcv",
                           number = nfolds,
                           repeats = nreps,
                           savePredictions = 'final',
                           allowParallel = TRUE,
                           classProbs = TRUE,
                           summaryFunction=twoClassSummary)

fit <- train(X, y, trControl = fitControl, method=clf_model, preProcess=pp_order)
print(fit)

resamps = resamples(list(fit=fit, tmp=fit))
auc_stats = summary(resamps)$statistics$ROC['fit',]
cnames = sapply(names(auc_stats), function(x) sprintf('AUC_%s', x))
names(auc_stats) = cnames
sens_stats = summary(resamps)$statistics$Sens['fit',]
cnames = sapply(names(sens_stats), function(x) sprintf('Sens_%s', x))
names(sens_stats) = cnames
spec_stats = summary(resamps)$statistics$Spec['fit',]
cnames = sapply(names(spec_stats), function(x) sprintf('Spec_%s', x))
names(spec_stats) = cnames
