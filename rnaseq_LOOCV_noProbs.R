args <- commandArgs(trailingOnly = TRUE)

library(caret)
library(doParallel)

if (length(args) > 0) {
    fname = args[1]
    myregion = args[2]
    clf_model = args[3]
    nfolds = as.numeric(args[4])
    nreps = as.numeric(args[5])
    ncores = as.numeric(args[6])
    out_file = args[7]
} else {
    fname = '~/data/rnaseq_derek/X_ACCnoPH_zv_nzv_center_scale.rds'
    myregion = 'ACC'
    clf_model = 'PenalizedLDA'
    ncores = 32
    nfolds = 10
    nreps = 10
    out_file = '/dev/null'
}

X = readRDS(fname)
just_target = readRDS('~/data/rnaseq_derek/data_from_philip.rds')
y = just_target[just_target$Region==myregion, 'Diagnosis']

my_summary = function(data, lev = NULL, model = NULL) {
    tcs = twoClassSummary(data, lev=lev)
    a = c((tcs['Sens'] + tcs['Spec'])/2, tcs)
    names(a)[1] = 'BalancedAccuracy'
    return(a)
}

registerDoParallel(ncores)
getDoParWorkers()

set.seed(42)
fitControl <- trainControl(method = "repeatedcv",
                           number = nfolds,
                           repeats = nreps,
                           savePredictions = 'final',
                           allowParallel = TRUE,
                           classProbs = FALSE,
                           summaryFunction=my_summary)

# let's then do a repeated 10 fold CV within LOOCV. We save the test predictions
# to later compute the overall result.
varimps = matrix(nrow=ncol(X), ncol=nrow(X))
test_preds = c()
for (test_rows in 1:5) {#length(y)) {
    print(sprintf('Hold out %d / %d', test_rows, length(y)))
    X_train <- X[-test_rows, ]
    X_test <- X[test_rows, ]
    y_train <- factor(y[-test_rows])
    y_test <- factor(y[test_rows])

    set.seed(42)
    fit <- train(X_train, y_train, trControl = fitControl, method = clf_model,
                 metric='BalancedAccuracy')

    preds_class = predict.train(fit, newdata=X_test)
    dat = data.frame(obs = y_test, pred = preds_class)
    test_preds = rbind(test_preds, dat)

    tmp = varImp(fit, useModel=T)$importance
    varimps[, test_rows] = tmp[,1]
}

mcs = my_summary(test_preds, lev=levels(y))
test_results = c(mcs['BalancedAccuracy'], mcs['Sens'], mcs['Spec'])
names(test_results) = c('test_BalancedAccuracy', 'test_Sens', 'test_Spec')

res = c(myregion, clf_model, nfolds, nreps, test_results)
line_res = paste(res,collapse=',')
write(line_res, file=out_file, append=TRUE)
print(line_res)

# export variable importance
a = rowMeans(varimps, na.rm=T)
names(a) = rownames(tmp)
out_dir = '~/data/rnaseq_derek/LOOCV/'
fname = sprintf('%s/varimp_%s_%s_%d_%d.csv',
                out_dir, myregion, clf_model, nfolds, nreps)
write.csv(a, file=fname)