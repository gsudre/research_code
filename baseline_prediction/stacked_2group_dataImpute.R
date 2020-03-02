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
    use_meds = T
    out_file = '/dev/null'
}

g1 = 'nonimp'
g2 = 'imp'

library(caret)
library(pROC)
data = readRDS(sprintf('~/data/baseline_prediction/prs_start/complete_massagedResids_clinDiffGE%d_02202020.rds', clin_diff))

print('Imputing all missing data...')
set.seed(42)
base_vars = c(colnames(data)[42:53], colnames(data)[74:81])
# anatomical
imp_vars = colnames(data)[66:73]
test = preProcess(data[, c(base_vars, imp_vars)], method = "bagImpute")
data[, c(base_vars, imp_vars)] <- predict(test, data[, c(base_vars, imp_vars)])
# beery, FSIQ, SES
imp_vars = c(colnames(data)[82], 'FSIQ', 'SES')
test = preProcess(data[, c(base_vars, imp_vars)], method = "bagImpute")
data[, c(base_vars, imp_vars)] <- predict(test, data[, c(base_vars, imp_vars)])
# wj
imp_vars = colnames(data)[87:88]
test = preProcess(data[, c(base_vars, imp_vars)], method = "bagImpute")
data[, c(base_vars, imp_vars)] <- predict(test, data[, c(base_vars, imp_vars)])
# wisc
imp_vars = colnames(data)[83:86]
test = preProcess(data[, c(base_vars, imp_vars)], method = "bagImpute")
data[, c(base_vars, imp_vars)] <- predict(test, data[, c(base_vars, imp_vars)])

if (my_sx == 'inatt') {
    phen = 'thresh0.00_inatt_GE6_wp05'
} else {
    phen = 'thresh0.50_hi_GE6_wp05'
}

domains = list(iq_vmi = c('FSIQ', "VMI.beery"),
               wisc = c("SSB.wisc", "SSF.wisc", 'DSF.wisc', 'DSB.wisc'),
               wj = c("DS.wj", "VM.wj"),
               demo = c('base_age', 'sex', 'SES'),
               gen = colnames(data)[42:53],
               dti = colnames(data)[74:81],
               anat = colnames(data)[66:73]
               )
if (use_clin) {
    domains[['clin']] = c('base_inatt', 'base_hi')
    if (use_meds) {
        domains[['clin']] = c(domains[['clin']], c('internalizing', 'externalizing',
                                                'medication_status_at_observation'))
    }
}

set.seed(42)
fitControl <- trainControl(method = "repeatedcv",
                           number = 10,
                           repeats = 10,
                           classProbs=T,
                           summaryFunction=twoClassSummary
                           )

adhd = data[, phen] == g2 | data[, phen] == g1
data2 = data[adhd, ]
data2[, phen] = factor(data2[, phen], ordered=F)
data2[, phen] = relevel(data2[, phen], ref=g1)
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
                                             tuneLength = 10, metric="ROC")',
                            dom)))
    eval(parse(text=sprintf('%s_preds = data.frame(g1=rep(NA, nrow(training)),
                                                   g2=rep(NA, nrow(training)))',
                            dom)))
    eval(parse(text=sprintf('preds = predict(%s_fit, type="prob")', dom)))
    eval(parse(text=sprintf('%s_preds[keep_me, ] = preds', dom)))
}
# ensemble training
preds_str = sapply(names(domains), function(d) sprintf('%s_preds[, 1]', d))
cbind_str = paste('prob_data = cbind(', paste(preds_str, collapse=','), ')',
                  sep="")
eval(parse(text=cbind_str))
colnames(prob_data) = names(domains)

set.seed(42)
ens_fit <- train(x = prob_data, y=training[, phen],
                 method = ens_model, trControl = fitControl, tuneLength = 10,
                 metric='ROC')
preds_class = predict(ens_fit)
preds_probs = predict(ens_fit, type='prob')
dat = cbind(data.frame(obs = training[, phen],
                 pred = preds_class), preds_probs)
res_train = twoClassSummary(dat, lev=colnames(preds_probs))

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
    print(sprintf('Testing on %d participants', nrow(this_data)))
    eval(parse(text=sprintf('%s_test_preds = data.frame(g1=rep(NA, nrow(testing)),
                                                   g2=rep(NA, nrow(testing)))', dom)))
    eval(parse(text=sprintf('preds = predict(%s_fit, type="prob", newdata=this_data)', dom)))
    eval(parse(text=sprintf('print(varImp(%s_fit))', dom)))
    eval(parse(text=sprintf('%s_test_preds[keep_me, ] = preds', dom)))
}
preds_str = sapply(names(domains), function(d) sprintf('%s_test_preds[, 1]', d))
cbind_str = paste('prob_test_data = cbind(', paste(preds_str, collapse=','), ')',
                  sep="")
eval(parse(text=cbind_str))
colnames(prob_test_data) = names(domains)

preds_class = predict(ens_fit, newdata=prob_test_data)
preds_probs = predict(ens_fit, newdata=prob_test_data, type='prob')
dat = cbind(data.frame(obs = testing[, phen],
                 pred = preds_class), preds_probs)
res = twoClassSummary(dat, lev=colnames(preds_probs))
print(res)
print(varImp(ens_fit))

line=sprintf("%s,%s,%s,%d,%s,%s,%d,%f,%f", my_sx, clf_model, ens_model,
             clin_diff, use_clin, use_meds,
             length(levels(training[,phen])), res_train['ROC'], res['ROC'])
print(line)
write(line, file=out_file, append=TRUE)
