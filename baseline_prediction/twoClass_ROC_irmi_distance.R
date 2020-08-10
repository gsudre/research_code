args <- commandArgs(trailingOnly = TRUE)

library(caret)

if (length(args) > 0) {
    fname = args[1]
    phen = args[2]
    c1 = args[3]
    c2 = args[4]
    clf_model = args[5]
    impute = args[6]
    use_covs = as.logical(args[7])
    out_file = args[8]
} else {
    fname = '~/data/baseline_prediction/FINAL_DATA_08072020_IRMI.csv'
    phen = 'categ_all_lm'
    c1 = 'stable'
    c2 = 'never_affected'
    clf_model = 'rf'
    mygrid=data.frame(mtry=2)
    impute = 'dti'
    use_covs = FALSE
    out_file = '/dev/null'
}

data = read.csv(fname)
data$sex_numeric = as.factor(data$sex_numeric)
# data$SES_group3 = as.factor(data$SES_group3)
data$base_total = data$base_inatt + data$base_hi

data = data[data$pass2_58=='yes',]

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
              'FSIQ', 'SS_RAW', 'DS_RAW', 'PS_STD', 'VMI.beery_STD',
            #   'FSIQ', 'SS_RAW', 'DS_RAW', 'PS_RAW', 'VMI.beery_RAW',
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

X = data3
y = factor(data2$phen)

# selecting only kids in the 2 specified groups
keep_me = y==c1 | y==c2
X = as.data.frame(X[keep_me, ])
y = factor(y[keep_me])

print(dim(X))
print(table(y))

X_train = c()
X_test = c()
y_train = c()
y_test = c()
for (t in c(c1, c2)) {
    # this refers to X
    candidates = which(y==t)
    while (length(candidates) >= 3) {
        X_group = scale(X[candidates,])
        # all indexes refer to X_group!
        dists = dist(data.frame(X_group), upper=T)
        closest = which(as.matrix(dists)==min(dists), arr.ind=T)
        X_test = rbind(X_test, X_group[closest[1], ])
        y_test = c(y_test, t)
        # get the kids most similar to our testing kid
        s = sort(as.matrix(dists)[closest[1],], index.return=T)
        # the first is always zero... select kids not chosen yet
        cnt = 2
        chosen = c()
        while ((length(chosen) < 2) && (cnt <= nrow(X_group))) {
            chosen = c(chosen, s$ix[cnt])
            y_train = c(y_train, t)
            cnt = cnt + 1
        }
        X_train = rbind(X_train, X_group[chosen,])
        # need to remove candidates based on X!
        candidates = candidates[-c(closest[1], chosen)]

    }
}
y_train = factor(y_train)
y_test = factor(y_test)

print(dim(X_train))
print(dim(X_test))
print(table(y_train))
print(table(y_test))

# imputation and feature engineering
set.seed(42)
pp_order = c('zv', 'nzv', 'corr', 'YeoJohnson', 'center', 'scale')
# pp_order = c('zv', 'nzv', 'bagImpute')
pp = preProcess(rbind(X_train, X_test), method = pp_order)
X_train = predict(pp, X_train)
X_test = predict(pp, X_test)

set.seed(42)
up_train <- upSample(x = X_train, y = y_train) 
X_train = up_train
X_train$Class = NULL
y_train = up_train$Class

model_weights = NULL
# model_weights <- ifelse(y_train == levels(y_train)[1],
#                         (1/table(y_train)[1]) * 0.5,
#                         (1/table(y_train)[2]) * 0.5)

# library(bestNormalize)
# for (v in setdiff(dummies$vars, dummies$facVars)) {
#     bn = orderNorm(X_train[, v])
#     X_train[, v] = bn$x.t
#     X_test[, v] = predict(bn, X_test[, v])
# }

# pp_order = c('corr', 'center')
# pp = preProcess(X_train, method = pp_order)
# X_train = predict(pp, X_train)
# X_test = predict(pp, X_test)

print(colnames(X_train))
print(table(y_train))
print(table(y_test))

set.seed(42)
fitControl <- trainControl(method = "none",
                           classProbs = TRUE,
                           summaryFunction=twoClassSummary)
# set.seed(42)
# fitControl <- trainControl(method = "repeatedcv", number=10, repeats=10,
#                         classProbs = TRUE,
#                         summaryFunction=twoClassSummary)

set.seed(42)
fit <- train(X_train, tuneGrid=mygrid,
                        y_train,
                        trControl = fitControl,
                        method = clf_model,
                        metric='ROC')

preds_class = predict.train(fit, newdata=X_test)
preds_probs = predict.train(fit, newdata=X_test, type='prob')
dat = cbind(data.frame(obs = y_test, pred = preds_class), preds_probs)
mcs = twoClassSummary(dat, lev=colnames(preds_probs))
test_results = c(mcs['ROC'], mcs['Sens'], mcs['Spec'])
names(test_results) = c('test_AUC', 'test_Sens', 'test_Spec')

res = c(phen, clf_model, c1, c2, impute, use_covs,
        test_results, table(y_train), table(y_test))
line_res = paste(res,collapse=',')
write(line_res, file=out_file, append=TRUE)

# export variable importance
a = varImp(fit, useModel=T)
b = varImp(fit, useModel=F)
split_fname = strsplit(x=out_file, split='/')[[1]]
myprefix = gsub(x=split_fname[length(split_fname)], pattern='.csv', replacement='')
out_dir = '~/data/baseline_prediction/more_models/'
fname = sprintf('%s/varimp_%s_%s_%s_%s_%s_%s_%s.csv',
                out_dir, myprefix, clf_model, phen, c1, c2, impute, use_covs)
# careful here because for non-linear models the rows of the importance matrix
# are not aligned!!!
write.csv(cbind(a$importance, b$importance), file=fname)
print(varImp(fit, useModel=F, scale=F))

# export fit
fname = sprintf('%s/fit_%s_%s_%s_%s_%s_%s_%s.RData',
                out_dir, myprefix, clf_model, phen, c1, c2, impute, use_covs)
save(fit, file=fname)

print(line_res)