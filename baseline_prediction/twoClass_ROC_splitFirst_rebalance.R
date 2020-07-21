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
    c2 = 'stable'
    clf_model = 'slda'
    impute = 'dti'
    ncores = 2
    use_covs = F
    out_file = '/dev/null'
}

data = read.csv(fname)
data$sex_numeric = as.factor(data$sex_numeric)
data$SES_group3 = as.factor(data$SES_group3)
# data$slf_fa = data$slf_all  # just to make it easier to filter out
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
X_train <- data2[train_rows, ]
X_test <- data2[-train_rows, ]
X_train$phen = NULL
X_test$phen = NULL
y_train <- data2[train_rows,]$phen
y_test <- data2[-train_rows,]$phen

set.seed(42)
pp_order = c('bagImpute')
pp = preProcess(X_train, method = pp_order)
X_train = predict(pp, X_train)
X_test = predict(pp, X_test)

# with imputation out of the way, we can go ahead and normalize them all
# together
X = rbind(X_train, X_test)

dummies = dummyVars(~., data=X, fullRank=T)
# normalize non-dummy variables
library(bestNormalize)
for (v in setdiff(dummies$vars, dummies$facVars)) {
    bn = orderNorm(X[, v])
    X[, v] = bn$x.t
}

# codify dummies
X = predict(dummies, newdata=X)
# imputation and feature engineering
set.seed(42)
pp_order = c('zv', 'nzv', 'corr', 'center', 'scale')
pp = preProcess(X, method = pp_order)
X = predict(pp, X)

# split everything again
X_train = X[1:nrow(X_train), ]
X_test = X[(nrow(X_train)+1):nrow(X), ]

# selecting only kids in the 2 specified groups
keep_me = y_train==c1 | y_train==c2
X_train = X_train[keep_me, ]
y_train = factor(y_train[keep_me])
keep_me = y_test==c1 | y_test==c2
X_test = X_test[keep_me, ]
y_test = factor(y_test[keep_me])

print(dim(X_train))

registerDoParallel(ncores)
getDoParWorkers()
set.seed(42)

fitControl <- trainControl(method = "none",
                           allowParallel = TRUE,
                           classProbs = TRUE,
                           summaryFunction=twoClassSummary)

# set.seed(42)
# up_train <- upSample(x = X_train, y = y_train, list=T) 
# X_train = up_train[[1]]
# y_train = up_train[[2]]
# fitControl$sampling='smote'
# model_weights <- ifelse(y_train == c1, (1/table(y_train)[1]) * 0.5,
#                         (1/table(y_train)[2]) * 0.5)

set.seed(42)
fit <- train(X_train,
                        y_train,
                        trControl = fitControl,
                        method = clf_model,)
                        # weights=model_weights)

preds_class = predict.train(fit, newdata=X_test)
preds_probs = predict.train(fit, newdata=X_test, type='prob')
dat = cbind(data.frame(obs = y_test, pred = preds_class), preds_probs)
mcs = twoClassSummary(dat, lev=colnames(preds_probs))
test_results = c(mcs['ROC'], mcs['Sens'], mcs['Spec'])
names(test_results) = c('test_AUC', 'test_Sens', 'test_Spec')

res = c(phen, clf_model, c1, c2, impute, use_covs, test_results)
line_res = paste(res,collapse=',')
write(line_res, file=out_file, append=TRUE)
print(line_res)

# # export variable importance
# a = varImp(fit, useModel=T)
# b = varImp(fit, useModel=F)
# out_dir = '~/data/baseline_prediction/splitFirstTwoClass/'
# fname = sprintf('%s/varimp_%s_%s_%s_%s_%s_%s_%d_%d.csv',
#                 out_dir, clf_model, phen, c1, c2, impute, use_covs, nfolds, nreps)
# # careful here because for non-linear models the rows of the importance matrix
# # are not aligned!!!
# write.csv(cbind(a$importance, b$importance), file=fname)

# # export fit
# fname = sprintf('%s/fit_%s_%s_%s_%s_%s_%s_%d_%d.RData',
#                 out_dir, clf_model, phen, c1, c2, impute, use_covs, nfolds, nreps)
# save(fit, file=fname)

# print(summary(y_train))
# print(summary(y_test))
# print(summary(train_rows))