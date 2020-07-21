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
    ncores = as.numeric(args[7])
    use_covs = as.logical(args[8])
    out_file = args[9]
} else {
    fname = '~/data/baseline_prediction/gf_JULY_ols_definition_GS.csv'
    phen = 'categ_all_lm'
    c1 = 'worsening'
    c2 = 'never_affected'
    clf_model = 'treebag'
    impute = 'dti'
    ncores = 2
    use_covs = TRUE
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
dummies = dummyVars(phen ~ ., data = data2)
data3 = predict(dummies, newdata = data2)

# selecting only kids in the 2 specified groups
keep_me = data2$phen==c1 | data2$phen==c2
data3 = data3[keep_me, ]
data2 = data2[keep_me, ]
data = data[keep_me, ]

# imputation and feature engineering
set.seed(42)
pp_order = c('zv', 'nzv', 'corr', 'YeoJohnson', 'center', 'scale', 'bagImpute')
pp = preProcess(data3, method = pp_order)
X = predict(pp, data3)
y = factor(data2$phen)

# remove linear combination variables
comboInfo <- findLinearCombos(X)
X = X[, -comboInfo$remove]

registerDoParallel(ncores)
getDoParWorkers()
set.seed(42)
fitControl <- trainControl(method = "none",
                           savePredictions = 'final',
                           allowParallel = TRUE,
                           classProbs = TRUE,
                           summaryFunction=twoClassSummary)
c1_idx = which(y == c1)
c2_idx = which(y == c2)
acc = 0
ntests = 0
for (i in c1_idx) {
    for (j in c2_idx) {
        Xtrain = X[-c(i, j), ]
        ytrain = y[-c(i, j)]
        fit <- train(Xtrain, ytrain, trControl = fitControl, method=clf_model)
        Xtest = X[c(i, j),]
        preds_probs = predict.train(fit, newdata=Xtest, type='prob')
        rownames(preds_probs) = c(c1, c2)
        # we want the diagonal probability sum to be bigger than off-diagonal
        if (preds_probs[c1,c1] + preds_probs[c2,c2] >
            preds_probs[c1,c2] + preds_probs[c2,c1]) {
                acc = acc + 1
        }
        ntests = ntests + 1
    } 
}

res = c(phen, clf_model, c1, c2, impute, use_covs, acc/ntests)
line_res = paste(res,collapse=',')

write(line_res, file=out_file, append=TRUE)
print(line_res)
