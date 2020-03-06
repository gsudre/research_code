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
    clf_model = 'cforest'
    clin_diff = 1
    use_clin = T
    use_meds = F
    out_file = '/dev/null'
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

training = data[data$bestInFamily, ]
testing = data[!data$bestInFamily, ]

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
            tuneLength = 10, metric="AUC")
preds_class = predict(fit, newdata=this_data)
preds_probs = predict(fit, newdata=this_data, type='prob')
dat = cbind(data.frame(obs = training[, phen],
                 pred = preds_class), preds_probs)
res_train = multiClassSummary(dat, lev=colnames(preds_probs))

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
res = multiClassSummary(dat, lev=colnames(preds_probs))
print(res)
print(varImp(fit))

print(sprintf('Testing on %d participants', nrow(this_data)))

line=sprintf("%s,%s,%s,%d,%s,%d,%f,%f", my_sx, clf_model,
             clin_diff, use_clin, use_meds,
             length(levels(training[,phen])), res_train['AUC'], res['AUC'])
print(line)
write(line, file=out_file, append=TRUE)
