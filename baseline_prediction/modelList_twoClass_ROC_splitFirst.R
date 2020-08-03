args <- commandArgs(trailingOnly = TRUE)

library(caret)
library(caretEnsemble)
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
    fname = '~/data/baseline_prediction/FINAL_DATA_to_gs_JULY_26_2020b.csv'
    phen = 'categ_all_lm'
    c1 = 'never_affected'
    c2 = 'stable'
    clf_model = 'svmRadialCost'
    impute = 'dti'
    nfolds = 5
    nreps = 10
    ncores = 2
    use_covs = FALSE
    out_file = '/dev/null'
}

data = read.csv(fname)
data$sex_numeric = as.factor(data$sex_numeric)
# data$SES_group3 = as.factor(data$SES_group3)
data$base_total = data$base_inatt + data$base_hi

data = data[data$pass2_58=='yes',]

# data$slf_fa = data$slf_all  # just to make it easier to filter out
var_names = c(
              # PRS
              'ADHD_PRS0.000100', 'ADHD_PRS0.001000',
              'ADHD_PRS0.010000', 'ADHD_PRS0.050000',
              'ADHD_PRS0.100000', 'ADHD_PRS0.200000',
              'ADHD_PRS0.300000', 'ADHD_PRS0.400000',
              'ADHD_PRS0.500000',
              # DTI
              'atr_fa', 'cst_fa', 'cing_cing_fa', 'cing_hipp_fa', 'cc_fa',
              'ilf_fa', 'slf_fa', 'unc_fa', 'ifo_fa',
              #   demo
              'sex_numeric', 'base_age',
                # 'SES_group3',
              # cog
              'FSIQ', 'SS_RAW', 'DS_RAW', 'PS_RAW', 'VMI.beery_RAW',
            #   # anat
              'cerbellum_white', 'cerebllum_grey', 'amygdala',
              'cingulate', 'lateral_PFC', 'OFC', 'striatum', 'thalamus',
              # base SX
              'base_inatt', 'base_hi'
            # 'age_onset'
            # 'last_age'
              )

covar_names = c(# DTI
                'norm.rot', 'norm.trans', # base_age, gender,
                # cog
                # 'base_age', 'sex_numeric',
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

# data2 = data2[data$ever_ADHD == 'include',]
# data = data[data$ever_ADHD == 'include',]

# data2 = data2[data$parent_history_include == 'yes',]
# data = data[data$parent_history_include == 'yes',]

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

# data2$slf_fa = NULL

# will need this later so training rows match data2
data = data[use_me, ]
data2$phen = as.factor(data[, phen])

dummies = dummyVars(phen ~ ., data = data2)
data3 = predict(dummies, newdata = data2)

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
# data3 doesn't have the target column!
X_train <- as.data.frame(data3[train_rows, ])
X_test <- as.data.frame(data3[-train_rows, ])
y_train <- data2[train_rows,]$phen
y_test <- data2[-train_rows,]$phen

# selecting only kids in the 2 specified groups
keep_me = y_train==c1 | y_train==c2
X_train = as.data.frame(X_train[keep_me, ])
y_train = factor(y_train[keep_me])
keep_me = y_test==c1 | y_test==c2
X_test = as.data.frame(X_test[keep_me, ])
y_test = factor(y_test[keep_me])

# imputation and feature engineering
set.seed(42)
pp_order = c('zv', 'nzv', 'corr', 'YeoJohnson', 'center', 'scale', 'bagImpute')
pp = preProcess(X_train, method = pp_order)
X_train = predict(pp, X_train)
X_test = predict(pp, X_test)

# remove linear combination variables
comboInfo <- findLinearCombos(X_train)
if (length(comboInfo$remove) > 0) {
    X_train = X_train[, -comboInfo$remove]
    X_test = X_test[, -comboInfo$remove]
}

print(colnames(X_train))
print(table(y_train))
print(table(y_test))

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

set.seed(42)
model_list <- caretList(X_train,
                        y_train,
                        trControl = fitControl,
                        methodList = c(clf_model, 'null'),
                        tuneList = NULL,
                        continue_on_fail = TRUE,
                        metric='ROC')

fit = model_list[[clf_model]]
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

preds_class = predict.train(fit, newdata=X_test)
preds_probs = predict.train(fit, newdata=X_test, type='prob')
dat = cbind(data.frame(obs = y_test, pred = preds_class), preds_probs)
mcs = twoClassSummary(dat, lev=colnames(preds_probs))
test_results = c(mcs['ROC'], mcs['Sens'], mcs['Spec'])
names(test_results) = c('test_AUC', 'test_Sens', 'test_Spec')

res = c(phen, clf_model, c1, c2, impute, use_covs, nfolds, nreps,
        auc_stats, sens_stats, spec_stats, test_results)
line_res = paste(res,collapse=',')
write(line_res, file=out_file, append=TRUE)
print(line_res)

# export variable importance
a = varImp(fit, useModel=T)
b = varImp(fit, useModel=F)
split_fname = strsplit(x=out_file, split='/')[[1]]
myprefix = gsub(x=split_fname[length(split_fname)], pattern='.csv', replacement='')
out_dir = '~/data/baseline_prediction/more_models/'
fname = sprintf('%s/varimp_%s_%s_%s_%s_%s_%s_%s_%d_%d.csv',
                out_dir, myprefix, clf_model, phen, c1, c2, impute, use_covs, nfolds, nreps)
# careful here because for non-linear models the rows of the importance matrix
# are not aligned!!!
write.csv(cbind(a$importance, b$importance), file=fname)
print(varImp(fit, useModel=F, scale=F))

# export fit
fname = sprintf('%s/fit_%s_%s_%s_%s_%s_%s_%s_%d_%d.RData',
                out_dir, myprefix, clf_model, phen, c1, c2, impute, use_covs, nfolds, nreps)
save(fit, file=fname)