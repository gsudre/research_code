args <- commandArgs(trailingOnly = TRUE)

library(caret)

if (length(args) > 0) {
    fname = args[1]
    phen = args[2]
    clf_model = args[3]
    impute = args[4]
    use_covs = as.logical(args[5])
    out_file = args[6]
} else {
    fname = '~/data/baseline_prediction/FINAL_DATA_08022020.csv'
    phen = 'categ_all_lm.1'
    clf_model = 'svmRadialSigma'
    impute = 'dti'
    use_covs = FALSE
    out_file = '/dev/null'
}

data = read.csv(fname)
data$sex_numeric = as.factor(data$sex_numeric)
# data$SES_group3 = as.factor(data$SES_group3)
data$base_total = data$base_inatt + data$base_hi

data = data[data$pass2_58=='yes',]
data = data[data$categ_all_lm.1!='never_affected',]

var_names = c(
            #   # PRS
            #   'ADHD_PRS0.000100', 'ADHD_PRS0.001000',
            #   'ADHD_PRS0.010000', 'ADHD_PRS0.050000',
            #   'ADHD_PRS0.100000', 'ADHD_PRS0.200000',
            #   'ADHD_PRS0.300000', 'ADHD_PRS0.400000',
            #   'ADHD_PRS0.500000',
            #   # DTI
            #   'atr_fa', 'cst_fa', 'cing_cing_fa', 'cing_hipp_fa', 'cc_fa',
            #   'ilf_fa', 'slf_fa', 'unc_fa', 'ifo_fa',
              #   demo
              'sex_numeric', 'base_age',
                # 'SES_group3',
              # cog
            #   'FSIQ', 'SS_RAW', 'DS_RAW', 'PS_STD', 'VMI.beery_STD',
            # # # #   'FSIQ', 'SS_RAW', 'DS_RAW', 'PS_RAW', 'VMI.beery_RAW',
            # #   # anat
            #   'cerbellum_white', 'cerebllum_grey', 'amygdala',
            #   'cingulate', 'lateral_PFC', 'OFC', 'striatum', 'thalamus',
              # base SX
              'base_inatt', 'base_hi'
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

# data2 = data2[data$EVER_ADHD == 'yes',]
# data = data[data$EVER_ADHD == 'yes',]

# data2 = data2[data$include_parental_history == 'yes',]
# data = data[data$include_parental_history == 'yes',]

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

data2$phen = as.factor(data[, phen])

# split traing and test between members of the same family
train_rows = c()
test_rows = c()
for (fam in unique(data$FAMID)) {
    fam_rows = which(data$FAMID == fam)
    if (length(fam_rows) == 1) {
        train_rows = c(train_rows, fam_rows[1])
    } else {
        # choose the oldest kid in the family for training, second oldest for
        # testing... throwing away everyone else
        age_sort = sort(data[fam_rows, 'base_age'], index.return=T, decreasing=T)
        train_rows = c(train_rows, fam_rows[age_sort$ix[1]])
        test_rows = c(test_rows, fam_rows[age_sort$ix[2:length(fam_rows)]])
    }
}

X = data3
y = factor(data2$phen)

test_preds = c()
for (test_rows in 1:length(y)) {
    print(sprintf('Hold out %d / %d', test_rows, length(y)))
    X_train <- X[-test_rows, ]
    X_test <- t(as.matrix(X[test_rows, ]))
    y_train <- y[-test_rows]
    y_test <- y[test_rows]

    set.seed(42)
    up_train <- upSample(x = X_train, y = y_train) 
    X_train = up_train
    X_train$Class = NULL
    y_train = up_train$Class

    # library(DMwR)
    # set.seed(42)
    # X2 = cbind(X_train, y_train)
    # up_train <- SMOTE(y_train ~ ., data = X2) 
    # X_train = up_train
    # X_train$y_train = NULL
    # y_train = up_train$y_train

    # library(ROSE)
    # set.seed(42)
    # X2 = cbind(X_train, y_train)
    # up_train <- ROSE(y_train ~ ., data  = X2)$data                         
    # X_train = up_train
    # X_train$y_train = NULL
    # y_train = up_train$y_train

    # imputation and feature engineering
    set.seed(42)
    pp_order = c('zv', 'nzv', 'corr', 'YeoJohnson', 'center', 'scale', 'knnImpute')
    pp = preProcess(X_train, method = pp_order)
    X_train = predict(pp, X_train)
    X_test = predict(pp, X_test)

    set.seed(42)
    fitControl <- trainControl(method = "repeatedcv", number=3, repeats=10,
                            classProbs = TRUE,
                            summaryFunction=multiClassSummary)
    # fitControl <- trainControl(method = "none",
    #                            classProbs = TRUE,
    #                            summaryFunction=twoClassSummary)

    mygrid=expand.grid(mtry = 1:5)
    # mygrid=expand.grid(ncomp = 1:2)#qrt(ncol(X_train)))
    # mygrid=expand.grid(C = c(.01, .1, 1, 10, 100))
    # mygrid=c()
    set.seed(42)
    fit <- train(X_train, #tuneGrid=mygrid,
                            y_train,
                            trControl = fitControl,
                            method = clf_model,
                            metric='AUC')

    preds_class = predict.train(fit, newdata=X_test)
    preds_probs = predict.train(fit, newdata=X_test, type='prob')
    dat = cbind(data.frame(obs = y_test, pred = preds_class), preds_probs)
    test_preds = rbind(test_preds, dat)

    # tmp = varImp(fit, useModel=T)$importance
    # varimps[, test_rows] = tmp[,1]
}

mcs = multiClassSummary(test_preds, lev=levels(y))
print(mcs)

test_results = c(mcs['AUC'], mcs['Mean_Sensitivity'], mcs['Mean_Specificity'])
names(test_results) = c('test_AUC', 'test_Sens', 'test_Spec')
res = c(phen, clf_model, impute, use_covs,
        test_results, table(y_train), table(y_test))
line_res = paste(res,collapse=',')
write(line_res, file=out_file, append=TRUE)


# export variable importance
a = varImp(fit, useModel=T)
b = varImp(fit, useModel=F)
split_fname = strsplit(x=out_file, split='/')[[1]]
myprefix = gsub(x=split_fname[length(split_fname)], pattern='.csv', replacement='')
out_dir = '~/data/baseline_prediction/more_models/'
fname = sprintf('%s/varimp_%s_%s_%s_%s_%s.csv',
                out_dir, myprefix, clf_model, phen, impute, use_covs)
# careful here because for non-linear models the rows of the importance matrix
# are not aligned!!!
write.csv(cbind(a$importance, b$importance), file=fname)
# print(varImp(fit, useModel=F, scale=F))

# export fit
fname = sprintf('%s/fit_%s_%s_%s_%s_%s.RData',
                out_dir, myprefix, clf_model, phen, impute, use_covs)
save(fit, file=fname)

print(line_res)