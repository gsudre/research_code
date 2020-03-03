args <- commandArgs(trailingOnly = TRUE)

if (length(args) > 0) {
    my_sx = args[1]
    clf_model = args[2]
    clin_diff = as.numeric(args[3])
    use_clin = as.logical(args[4])
    use_meds = as.logical(args[5])
    out_file = args[6]
} else {
    my_sx = 'hi'
    clf_model = 'hdda'
    clin_diff = 1
    use_clin = T
    use_meds = T
    out_file = '/dev/null'
}

g1 = 'nonimp'
g2 = 'imp'

library(caret)
library(pROC)
data = readRDS(sprintf('~/data/baseline_prediction/prs_start/complete_massagedResidsIRMI_clinDiffGE%d_03032020.rds', clin_diff))

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
        domains[['clin']] = c(domains[['clin']],
                              c('internalizing', 'externalizing',
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

var_names = c()
for (dom in names(domains)) {
    var_names = c(var_names, domains[[dom]])
}
this_data = training[, var_names]
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
fit <- train(x = this_data,
            y=training[, phen],
            method = clf_model,
            trControl = fitControl,
            tuneLength = 10, metric="ROC")
preds_class = predict(fit, newdata=this_data)
preds_probs = predict(fit, newdata=this_data, type='prob')
dat = cbind(data.frame(obs = training[, phen],
                 pred = preds_class), preds_probs)
res_train = twoClassSummary(dat, lev=colnames(preds_probs))

# testing
this_data = testing[, var_names]
scale_me = c()
for (v in colnames(this_data)) {
    if (!is.factor(this_data[, v])) {
        scale_me = c(scale_me, v)
    } else {
        this_data[, v] = as.numeric(this_data[, v])
    }
}
this_data[, scale_me] = scale(this_data[, scale_me])
preds_class = predict(fit, newdata=this_data)
preds_probs = predict(fit, newdata=this_data, type='prob')
dat = cbind(data.frame(obs = testing[, phen],
                 pred = preds_class), preds_probs)
res = twoClassSummary(dat, lev=colnames(preds_probs))
print(res)
# print(varImp(fit))

line=sprintf("%s,%s,%s,%d,%s,%d,%f,%f", my_sx, clf_model,
             clin_diff, use_clin, use_meds,
             length(levels(training[,phen])), res_train['ROC'], res['ROC'])
print(line)
write(line, file=out_file, append=TRUE)
