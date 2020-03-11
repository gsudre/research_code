args <- commandArgs(trailingOnly = TRUE)

if (length(args) > 0) {
    my_sx = args[1]
    clf_model = args[2]
    clin_diff = as.numeric(args[3])
    use_clin = as.logical(args[4])
    use_meds = as.logical(args[5])
    nreps = as.numeric(args[6])
    nfolds = as.numeric(args[7])
    out_file = args[8]
} else {
    my_sx = 'hi'
    clf_model = 'kernelpls'
    clin_diff = 1
    use_clin = T
    use_meds = F
    nreps = 5
    nfolds = 5
    out_file = '/dev/null'
}

g1 = 'nonimp'
g2 = 'imp'

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
                           summaryFunction=twoClassSummary
                           )

adhd = data[, phen] == g2 | data[, phen] == g1
data2 = data[adhd, ]
data2[, phen] = factor(data2[, phen], ordered=F)
data2[, phen] = relevel(data2[, phen], ref=g1)

# if imputation is fair game before we split, so is scaling
var_names = c()
for (dom in names(domains)) {
    var_names = c(var_names, domains[[dom]])
}
scale_me = c()
for (v in var_names) {
    if (!is.factor(data2[, v])) {
        scale_me = c(scale_me, v)
    } else {
        data2[, v] = as.numeric(data2[, v])
    }
}
data2[, scale_me] = scale(data2[, scale_me])

set.seed(42)
training = data2
ctl = createMultiFolds(training[, phen], k=nfolds, times=nreps)

set.seed(42)
fitControl <- trainControl(method = "LOOCV",
                           classProbs=T,
                           summaryFunction=twoClassSummary
                           )

results = list()
importances = list()
for (rep in 1:nreps) {
    for (fold in 1:nfolds) {
        if (nfolds >= 10) {
            fold_name = sprintf('Fold%02d', fold)
        } else {
            fold_name = sprintf('Fold%d', fold)
        }
        if (nreps >= 10) {
            rep_name = sprintf('Rep02%d', rep)
        } else {
            rep_name = sprintf('Rep%d', rep)
        }
        fold_name = sprintf('%s.%s', fold_name, rep_name)
        print(fold_name)

        fold_rows = ctl[[fold_name]]
        ftrain = training[fold_rows,]
        ftest = training[-fold_rows,]

        fit <- train(x=ftrain[, var_names],
                     y=ftrain[, phen],
                     method = clf_model,
                     trControl = fitControl,
                     tuneLength = 10, metric="ROC")
        preds_class = predict(fit, newdata=ftest[, var_names])
        preds_probs = predict(fit, newdata=ftest[, var_names], type='prob')
        dat = cbind(data.frame(obs = ftest[, phen],
                               pred = preds_class), preds_probs)
        res = twoClassSummary(dat, lev=colnames(preds_probs))
        results[[fold_name]] = res
        importances[[fold_name]] = varImp(fit)
    }
}
       
mean_res = apply(as.data.frame(results), 1, mean)
sd_res = apply(as.data.frame(results), 1, sd)

line=sprintf("%s,%s,%d,%s,%s,%d,%f,%f", my_sx, clf_model,
             clin_diff, use_clin, use_meds,
             length(levels(training[,phen])), mean_res['ROC'], sd_res['ROC'])
print(line)
write(line, file=out_file, append=TRUE)
