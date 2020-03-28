args <- commandArgs(trailingOnly = TRUE)

library(caret)
library(caretEnsemble)
library(doParallel)

if (length(args) > 0) {
    fname = args[1]
    phen = args[2]
    clf_model = args[3]
    impute = args[4]
    nfolds = as.numeric(args[5])
    nreps = as.numeric(args[6])
    ncores = as.numeric(args[7])
    use_covs = as.logical(args[8])
    out_file = args[9]
} else {
    fname = '~/data/baseline_prediction/prs_start/gf_philip_03282020.csv'
    phen = 'categ_inatt3'
    clf_model = 'kernelpls'
    impute = 'dti'
    nfolds = 10
    nreps = 10
    ncores = 2
    use_covs = FALSE
    out_file = '/dev/null'
}

data = read.csv(fname)
data$sex_numeric = as.factor(data$sex_numeric)
data$SES_group3 = as.factor(data$SES_group3)
data$slf_fa = data$slf_all  # just to make it easier to filter out
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

data2$phen = as.factor(data[use_me, phen])
dummies = dummyVars(phen ~ ., data = data2)
data3 = predict(dummies, newdata = data2)

# split traing and test between members of the same family
train_rows = c()
for (fam in unique(data$FAMID)) {
    fam_rows = which(data$FAMID == fam)
    if (length(fam_rows) == 1) {
        train_rows = c(train_rows, fam_rows[1])
    } else {
        # choose the youngest kid in the family for training
        train_rows = c(train_rows,
                       fam_rows[which.max(data[fam_rows, 'base_age'])])
    }
}
# data3 doesn't have the target column!
X_train <- data3[train_rows, ]
X_test <- data3[-train_rows, ]
y_train <- data2[train_rows,]$phen
y_test <- data2[-train_rows,]$phen

# imputation and feature engineering
pp_order = c('zv', 'nzv', 'corr', 'YeoJohnson', 'center', 'scale', 'bagImpute')
pp = preProcess(X_train, method = pp_order)
X_train = predict(pp, X_train)
X_test = predict(pp, X_test)

registerDoParallel(ncores)
getDoParWorkers()
set.seed(42)
fitControl <- trainControl(method = "repeatedcv",
                           number = nfolds,
                           repeats = nreps,
                           savePredictions = 'final',
                           allowParallel = TRUE,
                           classProbs = TRUE,
                           summaryFunction=multiClassSummary)

set.seed(42)
model_list <- caretList(X_train,
                        y_train,
                        trControl = fitControl,
                        methodList = c(clf_model, 'null'),
                        tuneList = NULL,
                        continue_on_fail = TRUE,
                        metric='AUC')

options(digits = 3)
train_results = c(model_list$null$results$AUC)
test_results = c()
for (m in names(model_list)) {
    if (m != 'null') {
        train_results = c(mean(model_list[[m]]$results$AUC), train_results)
    }
    preds_class = predict.train(model_list[[m]], newdata=X_test)
    preds_probs = predict.train(model_list[[m]], newdata=X_test, type='prob')
    dat = cbind(data.frame(obs = y_test, pred = preds_class), preds_probs)
    test_results = c(test_results,
                     multiClassSummary(dat, lev=colnames(preds_probs))['AUC'])
}
names(train_results) = names(model_list)
names(test_results) = names(model_list)

line=sprintf("%s,%s,%s,%s,%d,%d,%f,%f,%f,%f,%f", phen, clf_model, impute,
             use_covs, nfolds, nreps, train_results[clf_model],
             sd(model_list[[clf_model]]$results$AUC),
             train_results['null'], test_results[clf_model],
             test_results['null'])
print(line)
write(line, file=out_file, append=TRUE)

# export variable importance
fit = model_list[[clf_model]]
a = varImp(fit, useModel=T)
b = varImp(fit, useModel=F)
out_dir = '~/data/baseline_prediction/prs_start/multiClass/'
fname = sprintf('%s/varimp_%s_%s_%s_%s_%d_%d.csv',
                out_dir, clf_model, phen, impute, use_covs, nfolds, nreps)
write.csv(cbind(a$importance, b$importance), file=fname)

# export fit
fname = sprintf('%s/fit_%s_%s_%s_%s_%d_%d.RData',
                out_dir, clf_model, phen, impute, use_covs, nfolds, nreps)
save(fit, file=fname)