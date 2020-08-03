args <- commandArgs(trailingOnly = TRUE)

library(caret)

if (length(args) > 0) {
    fname = args[1]
    phen = args[2]
    c1 = args[3]
    clf_model = args[4]
    impute = args[5]
    use_covs = as.logical(args[6])
    out_file = args[7]
} else {
    fname = '~/data/baseline_prediction/FINAL_DATA_08022020.csv'
    phen = 'categ_all_lm'
    c1 = 'never_affected'
    clf_model = 'slda'
    impute = 'dti'
    use_covs = FALSE
    out_file = '/dev/null'
}

data = read.csv(fname)
data$sex_numeric = as.factor(data$sex_numeric)
# data$SES_group3 = as.factor(data$SES_group3)
data$base_total = data$base_inatt + data$base_hi

data = data[data$pass2_58=='yes',]
# data = data[data[, phen] != 'never_affected', ]

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
            #   'FSIQ', 'SS_RAW', 'DS_RAW', 'PS_STD', 'VMI.beery_STD',
            #   # anat
              'cerbellum_white', 'cerebllum_grey', 'amygdala',
              'cingulate', 'lateral_PFC', 'OFC', 'striatum', 'thalamus'
              # base SX
            #   'base_inatt', 'base_hi'
            # 'base_total'
            # 'age_onset'
            # 'last_age'
              )

covar_names = c(# DTI
                'norm.rot', 'norm.trans',
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

if (impute == 'dti') {
    use_me = !is.na(data$slf_fa)
    data2 = data2[use_me, ]
    print(sprintf('Using %d observations, %d predictors.', nrow(data2),
                  ncol(data2))) 
} else if (impute == 'anat') {
    use_me = !is.na(data$thalamus)
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

dummies = dummyVars( ~ ., data = data2, fullRank=T)
data3 = predict(dummies, newdata = data2)

y = as.character(data[, phen])

keep_me = y==c1
y[!keep_me] = 'others'
y = factor(y)
X = data3

set.seed(42)
pp_order = c('center', 'scale', 'medianImpute')
fitControl <- trainControl(method = "loocv",
                           classProbs = TRUE,
                           summaryFunction=twoClassSummary)
                        #    sampling='none')
fit <- train(X, y, trControl = fitControl, preProcess=pp_order,
                 method = clf_model)
print(summary(fit))


# test_preds = c()
# for (test_rows in 1:length(y)) {
#     print(sprintf('Hold out %d / %d', test_rows, length(y)))
#     X_train <- X[-test_rows, ]
#     X_test <- t(as.matrix(X[test_rows, ]))
#     y_train <- factor(y[-test_rows])
#     y_test <- y[test_rows]

#     # only use the nonNA predictors of the test example
#     use_vars = which(!is.na(X_test))
#     X_train = X_train[, use_vars]
#     X_test = t(as.matrix(X_test[, use_vars]))
#     # set.seed(42)
#     # X2 = cbind(X_train, y_train)
#     # up_train <- SMOTE(y_train ~ ., data = X2) 
#     # X_train = up_train
#     # X_train$y_train = NULL
#     # y_train = up_train$y_train

#     # set.seed(42)
#     # up_train <- upSample(x = X_train, y = y_train) 
#     # X_train = up_train
#     # X_train$Class = NULL
#     # y_train = up_train$Class

#     # set.seed(42)
#     # X2 = cbind(X_train, y_train)
#     # up_train <- ROSE(y_train ~ ., data  = X2)$data                         
#     # X_train = up_train
#     # X_train$y_train = NULL
#     # y_train = up_train$y_train

#     idx = y_train==c1
#     pvals = sapply(1:ncol(X_train),
#                    function(x) {t.test(X_train[idx, x],
#                                            X_train[!idx, x])$p.value})
#     spvals = sort(pvals, index.return=T)
#     good_vars = spvals$ix[1:min(10, length(use_vars))]
#     fit <- train(X_train[, good_vars], y_train, trControl = fitControl,
#                  method = clf_model)
    
#     preds_class = predict.train(fit, newdata=t(as.matrix(X_test[, good_vars])))
#     preds_probs = predict.train(fit, newdata=t(as.matrix(X_test[, good_vars])), type='prob')
#     dat = cbind(data.frame(obs = y_test, pred = preds_class), preds_probs)
#     test_preds = rbind(test_preds, dat)

#     # tmp = varImp(fit, useModel=T)$importance
#     # varimps[, test_rows] = tmp[,1]
# }

# mcs = twoClassSummary(test_preds, lev=levels(y))
