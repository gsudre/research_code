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
    clf_model = 'spls'
    ncores = 2
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
                           classProbs = TRUE,
                           summaryFunction=my_summary)

ypos = which(y == levels(y)[1])
yneg = which(y == levels(y)[2])
test_rows = c()
for (p in ypos) {
    for (n in yneg) {
        test_rows = rbind(test_rows, c(p, n))
    }
}

# let's then do a repeated 10 fold CV within LOOCV. We save the test predictions
# to later compute the overall result.
varimps = matrix(nrow=ncol(X), ncol=nrow(test_rows))
acc = 0
for (trow in 1:nrow(test_rows)) {
    print(sprintf('Hold out %d / %d', trow, nrow(test_rows)))
    X_train <- X[-test_rows[trow,], ]
    X_test <- X[test_rows[trow,], ]
    y_train <- factor(y[-test_rows[trow,]])

    set.seed(42)
    fit <- train(X_train, y_train, trControl = fitControl, method = clf_model,
                 metric='BalancedAccuracy')

    preds_probs = predict.train(fit, newdata=X_test, type='prob')
    # first observation in test is always Case and second is Control
    if ((preds_probs[1, 'Case'] > preds_probs[2, 'Case']) ||
        (preds_probs[1, 'Control'] < preds_probs[2, 'Control'])) {
            acc = acc + 1
    }

    tmp = varImp(fit, useModel=T)$importance
    varimps[, trow] = tmp[,1]
}

res = c(myregion, clf_model, nfolds, nreps, acc/nrow(test_rows))
line_res = paste(res,collapse=',')
write(line_res, file=out_file, append=TRUE)
print(line_res)

# export variable importance
a = rowMeans(varimps, na.rm=T)
names(a) = rownames(tmp)
out_dir = '~/data/rnaseq_derek/twoVtwo/'
fname = sprintf('%s/varimp_%s_%s_%d_%d.csv',
                out_dir, myregion, clf_model, nfolds, nreps)
write.csv(a, file=fname)