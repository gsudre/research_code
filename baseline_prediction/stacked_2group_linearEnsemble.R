#args <- commandArgs(trailingOnly = TRUE)
#my_sx = args[1]
#clf_model = args[2]
#ens_model = args[3]
#out_file = args[4]

my_sx = 'hi'
#my_sx = 'inatt'
clf_model = 'hdda'
ens_model = 'rpart2'

library(caret)
library(pROC)
data = readRDS('~/data/baseline_prediction/prs_start/complete_massagedResids_clinDiffGE1_02202020.rds')

min_sx = 6
for (sx in c('inatt', 'hi')) {
    if (sx == 'inatt') {
        thresh = 0
    } else if (sx == 'hi') {
        thresh = -.5
    }
    phen_slope = sprintf('slope_%s_GE%d_wp05', sx, min_sx)
    phen = sprintf('thresh%.2f_%s_GE%d_wp05', abs(thresh), sx, min_sx)
    data[, phen] = 'notGE6adhd'
    my_nvs = which(is.na(data[, phen_slope]))
    idx = data[my_nvs, 'base_inatt'] <= 2 & data[my_nvs, 'base_hi'] <= 2
    data[my_nvs[idx], phen] = 'nv012'
    data[which(data[, phen_slope] < thresh), phen] = 'imp'
    data[which(data[, phen_slope] >= thresh), phen] = 'nonimp'
    data[, phen] = factor(data[, phen], ordered=F)
    data[, phen] = relevel(data[, phen], ref='nv012')
    ophen = sprintf('ORDthresh%.2f_%s_GE%d_wp05', abs(thresh), sx, min_sx)
    data[, ophen] = factor(data[, phen],
                         levels=c('nv012', 'notGE6adhd', 'imp', 'nonimp'),
                         ordered=T)
}

if (my_sx == 'inatt') {
    phen = 'thresh0.00_inatt_GE6_wp05'
} else {
    phen = 'thresh0.50_hi_GE6_wp05'
}

# this is for the residualized data
domains = list(iq_vmi = c('FSIQ', "VMI.beery"),
               wisc = c("SSB.wisc", "SSF.wisc", 'DSF.wisc', 'DSB.wisc'),
               wj = c("DS.wj", "VM.wj"),
               demo = c('base_age', 'sex', 'SES'),
               clin = c('internalizing', 'externalizing',
                        'medication_status_at_observation', 'base_inatt', 'base_hi'),
               gen = colnames(data)[42:53],
               dti = colnames(data)[74:81],
               anat = colnames(data)[66:73]
               )

# this is for the non-residualized data
# domains = list(iq_vmi = c('FSIQ', "VMI.beery"),
#                wisc = c("SSB.wisc", "SSF.wisc", 'DSF.wisc', 'DSB.wisc'),
#                wj = c("DS.wj", "VM.wj"),
#                demo = c('base_age', 'sex', 'SES'),
#                clin = c('internalizing', 'externalizing',
#                         'medication_status_at_observation',
#                         sprintf('base_%s', my_sx)),
#                gen = c(colnames(data)[38:49], colnames(data)[86:95]),
#                dti = colnames(data)[107:121],
#                anat = colnames(data)[96:106]
#                )
set.seed(42)
fitControl <- trainControl(method = "repeatedcv",
                           number = 10,
                           repeats = 10,
                           classProbs=T,
                           summaryFunction=twoClassSummary
                           )

adhd = data[, phen] == 'nonimp' | data[, phen] == 'imp'
data2 = data[adhd, ]
data2[, phen] = factor(data2[, phen], ordered=F)
data2[, phen] = relevel(data2[, phen], ref='imp')
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
    set.seed(42)
    eval(parse(text=sprintf('%s_fit <- train(x = this_data,
                                             y=training[keep_me, phen],
                                             method = clf_model,
                                             trControl = fitControl,
                                             tuneLength = 10, metric="ROC")',
                            dom)))
    eval(parse(text=sprintf('%s_preds = data.frame(imp=rep(NA, nrow(training)),
                                                   nonimp=rep(NA, nrow(training)))',
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

# prob_data[is.na(prob_data)] = .5

class1_ratio = table(training[, phen])[1]/nrow(training)
prob_data[is.na(prob_data)] = class1_ratio

# ipt = preProcess(prob_data, method = "bagImpute")
# prob_data = predict(ipt, prob_data)

set.seed(42)
ens_fit <- train(x = prob_data, y=training[, phen],
                 method = ens_model, trControl = fitControl, tuneLength = 10,
                 metric='ROC')
print(ens_fit)
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
    eval(parse(text=sprintf('%s_test_preds = data.frame(imp=rep(NA, nrow(testing)),
                                                   nonimp=rep(NA, nrow(testing)))', dom)))
    eval(parse(text=sprintf('preds = predict(%s_fit, type="prob", newdata=this_data)', dom)))
    eval(parse(text=sprintf('print(varImp(%s_fit))', dom)))
    eval(parse(text=sprintf('%s_test_preds[keep_me, ] = preds', dom)))
}
preds_str = sapply(names(domains), function(d) sprintf('%s_test_preds[, 1]', d))
cbind_str = paste('prob_test_data = cbind(', paste(preds_str, collapse=','), ')',
                  sep="")
eval(parse(text=cbind_str))
colnames(prob_test_data) = names(domains)

# prob_test_data[is.na(prob_test_data)] = .5
prob_test_data[is.na(prob_test_data)] = class1_ratio
# prob_test_data = predict(ipt, prob_test_data)

preds_class = predict(ens_fit, newdata=prob_test_data)
preds_probs = predict(ens_fit, newdata=prob_test_data, type='prob')
dat = cbind(data.frame(obs = testing[, phen],
                 pred = preds_class), preds_probs)
res = twoClassSummary(dat, lev=colnames(preds_probs))
print(varImp(ens_fit))

line=sprintf("%s,%s,%s,%f,%f", my_sx, clf_model, ens_model, res_train['ROC'],
             res['ROC'])
print(line)
write(line, file=out_file, append=TRUE)
