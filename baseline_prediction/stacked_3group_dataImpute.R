args <- commandArgs(trailingOnly = TRUE)

if (length(args) > 0) {
    my_sx = args[1]
    clf_model = args[2]
    ens_model = args[3]
    clin_diff = as.numeric(args[4])
    use_clin = as.logical(args[5])
    use_meds = as.logical(args[6])
    out_file = args[7]
} else {
    my_sx = 'hi'
    clf_model = 'hdda'
    ens_model = 'C5.0Tree'
    clin_diff = 1
    use_clin = T
    use_meds = F
    out_file = '/dev/null'
}

# had to hack the varImp in
# https://github.com/topepo/caret/blob/master/models/files/kernelpls.R because
# it was breaking with more than 2 classes
myVarImp = function(train_object) {
    library(pls)
    object = train_object$finalModel
    modelCoef <- coef(object, intercept = FALSE, comps = 1:object$ncomp)
    perf <- MSEP(object)$val

    nms <- dimnames(perf)
    if(length(nms$estimate) > 1) {
        pIndex <- if(is.null(estimate)) 1 else which(nms$estimate == estimate)
        perf <- perf[pIndex,,,drop = FALSE]
    }
    numResp <- dim(modelCoef)[2]

    if(numResp <= 2) {
        modelCoef <- modelCoef[,1,,drop = FALSE]
        perf <- perf[,1,]
        delta <- -diff(perf)
        delta <- delta/sum(delta)
        out <- data.frame(Overall = apply(abs(modelCoef), 1,
                                        weighted.mean, w = delta))
    } else {
        perf <- -t(apply(perf[1,,], 1, diff))
        perf <- t(apply(perf, 1, function(u) u/sum(u)))
        out <- matrix(NA, ncol = numResp, nrow = dim(modelCoef)[1])

        for(i in 1:numResp) {
            tmp <- abs(modelCoef[,i,, drop = FALSE])
            if (object$ncomp == 1) {
                out[,i] <- apply(tmp, 1,  weighted.mean, w = perf[, i])
            } else {
                out[,i] <- apply(tmp, 1,  weighted.mean, w = perf[i,])
            }
        }
        colnames(out) <- dimnames(modelCoef)[[2]]
        rownames(out) <- dimnames(modelCoef)[[1]]
    }
    as.data.frame(out)
}

library(caret)
library(pROC)
data = readRDS(sprintf('~/data/baseline_prediction/prs_start/complete_massagedRawNeuropsychResidsNoComorbiditiesIRMI_clinDiffGE%d_03062020.rds', clin_diff))

phen = sprintf('threshMED_%s_GE6_wp05', my_sx)

domains = list(iq_vmi = c('FSIQ', "VMI.beery"),
               wisc = c("SSB.wisc", "SSF.wisc", 'DSF.wisc', 'DSB.wisc'),
               wj = c("DS.wj", "VM.wj"),
               demo = c('base_age', 'sex', 'SES'),
               gen = colnames(data)[51:62],
               dti = colnames(data)[83:90],
               anat = colnames(data)[75:82]
               )
if (use_clin) {
    domains[['clin']] = c('base_inatt', 'base_hi')
    if (use_meds) {
        domains[['clin']] = c(domains[['clin']],
                              'medication_status_at_observation')
    }
}

set.seed(42)
fitControl <- trainControl(method = "repeatedcv",
                           number = 10,
                           repeats = 10,
                           classProbs=T,
                           summaryFunction=multiClassSummary
                           )

adhd = data[, phen] != 'nv012'
data2 = data[adhd, ]
data2[, phen] = factor(data2[, phen], ordered=F)
data2[, phen] = relevel(data2[, phen], ref='notGE6adhd')
training = data2[data2$bestInFamily, ]
testing = data2[!data2$bestInFamily, ]

for (dom in names(domains)) {
    print(sprintf('Training %s on %s (sx=%s, model=%s)', dom, phen, my_sx, clf_model))
    var_names = domains[[dom]]
    numNAvars = rowSums(is.na(training[, var_names]))
    keep_me = numNAvars == 0
    this_data = training[keep_me, var_names]
    scale_me = c()
    for (v in colnames(this_data)) {
        if (!is.factor(this_data[, v])) {
            scale_me = c(scale_me, v)
        } else {
            this_data[, v] = as.numeric(this_data[, v])
        }
    }
    this_data[, scale_me] = scale(this_data[, scale_me])
    print(sprintf('Training on %d participants', nrow(this_data)))
    set.seed(42)
    eval(parse(text=sprintf('%s_fit <- train(x = this_data,
                                             y=training[keep_me, phen],
                                             method = clf_model,
                                             trControl = fitControl,
                                             tuneLength = 10, metric="AUC")',
                            dom)))
    eval(parse(text=sprintf('%s_preds = data.frame(imp=rep(NA, nrow(training)),
                                                   nonimp=rep(NA, nrow(training)),
                                                   notGE6adhd=rep(NA, nrow(training)))',
                            dom)))
    eval(parse(text=sprintf('preds = predict(%s_fit, type="prob")', dom)))
    eval(parse(text=sprintf('%s_preds[keep_me, ] = preds', dom)))
}
# ensemble training
preds_str = sapply(names(domains), function(d) sprintf('%s_preds[, 1:2]', d))
cbind_str = paste('prob_data = cbind(', paste(preds_str, collapse=','), ')',
                  sep="")
eval(parse(text=cbind_str))
prob_header = c()
for (dom in names(domains)) {
    for (g in colnames(preds)[1:2]) {
        prob_header = c(prob_header, sprintf('%s_%s', dom, g))
    }
}
colnames(prob_data) = prob_header

ens_fit <- train(x = prob_data, y=training[, phen],
                 method = ens_model, trControl = fitControl, tuneLength = 10,
                 metric='AUC')
preds_class = predict(ens_fit)
preds_probs = predict(ens_fit, type='prob')
dat = cbind(data.frame(obs = training[, phen],
                 pred = preds_class), preds_probs)
res_train = multiClassSummary(dat, lev=colnames(preds_probs))

print(res_train)

# testing
for (dom in names(domains)) {
    print(dom)
    eval(parse(text=sprintf('var_names = colnames(%s_fit$trainingData)', dom)))
    # remove .outcome
    var_names = var_names[1:(length(var_names)-1)]
    numNAvars = rowSums(is.na(testing[, var_names]))
    keep_me = numNAvars == 0
    this_data = testing[keep_me, var_names]
    scale_me = c()
    for (v in colnames(this_data)) {
        if (!is.factor(this_data[, v])) {
            scale_me = c(scale_me, v)
        } else {
            this_data[, v] = as.numeric(this_data[, v])
        }
    }
    this_data[, scale_me] = scale(this_data[, scale_me])
    eval(parse(text=sprintf('%s_test_preds = data.frame(imp=rep(NA, nrow(testing)),
                                                   nonimp=rep(NA, nrow(testing)),
                                                   notGE6adhd=rep(NA, nrow(testing)))', dom)))
    eval(parse(text=sprintf('preds = predict(%s_fit, type="prob", newdata=this_data)', dom)))
    # eval(parse(text=sprintf('print(myVarImp(%s_fit))', dom)))
    eval(parse(text=sprintf('%s_test_preds[keep_me, ] = preds', dom)))
}
preds_str = sapply(names(domains), function(d) sprintf('%s_test_preds[, 1:2]', d))
cbind_str = paste('prob_test_data = cbind(', paste(preds_str, collapse=','), ')',
                  sep="")
eval(parse(text=cbind_str))
colnames(prob_test_data) = prob_header

preds_class = predict(ens_fit, newdata=prob_test_data)
preds_probs = predict(ens_fit, newdata=prob_test_data, type='prob')
dat = cbind(data.frame(obs = testing[, phen],
                 pred = preds_class), preds_probs)
res = multiClassSummary(dat, lev=colnames(preds_probs))
print(res)
# print(varImp(ens_fit))

line=sprintf("%s,%s,%s,%d,%s,%s,%d,%f,%f", my_sx, clf_model, ens_model,
             clin_diff, use_clin, use_meds,
             length(levels(training[,phen])), res_train['AUC'], res['AUC'])
print(line) 
write(line, file=out_file, append=TRUE)