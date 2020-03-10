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
    clf_model = 'kernelpls'
    ens_model = 'plr'
    clin_diff = 1
    use_clin = T
    use_meds = F
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
fitControl <- trainControl(method = "LOOCV",
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
nreps = 10
nfolds = 10
# training = data2[data2$bestInFamily, ]
# testing = data2[!data2$bestInFamily, ]
training = data2
ctl = createMultiFolds(training[, phen], k=nfolds, times=nreps)

results = list()
for (rep in 1:nreps) {
    for (fold in 1:nfolds) {
        fold_name = sprintf('Fold%d.Rep%d', fold, rep)
        fold_rows = ctl[[fold_name]]
        ftrain = training[fold_rows,]
        ftest = training[-fold_rows,]
        for (dom in names(domains)) {
            print(sprintf('Training %s (sx=%s, model=%s, fold=%d, rep=%d)',
                  dom, my_sx, clf_model, fold, rep))
            var_names = domains[[dom]]
            numNAvars = rowSums(is.na(ftrain[, var_names]))
            keep_me = numNAvars == 0
            this_data = ftrain[keep_me, var_names]
            
            set.seed(42)
            eval(parse(text=sprintf('%s_fit <- train(x=this_data,
                                                     y=ftrain[keep_me, phen],
                                                     method = clf_model,
                                                     trControl = fitControl,
                                                     tuneLength = 10,
                                                     metric="ROC")',
                                    dom)))
            eval(parse(text=sprintf('%s_preds = data.frame(g1=rep(NA,
                                                                  nrow(ftrain)),
                                                           g2=rep(NA,
                                                                  nrow(ftrain)))',
                                    dom)))
            eval(parse(text=sprintf('preds = predict(%s_fit, type="prob")',
                                    dom)))
            eval(parse(text=sprintf('%s_preds[keep_me, ] = preds', dom)))
        }
        # ensemble training
        print(sprintf('Training %s ensemble', ens_model))
        preds_str = sapply(names(domains),
                           function(d) sprintf('%s_preds[, 1]', d))
        cbind_str = paste('prob_data = cbind(',
                          paste(preds_str, collapse=','), ')',
                          sep="")
        eval(parse(text=cbind_str))
        colnames(prob_data) = names(domains)

        set.seed(42)
        ens_fit <- train(x = prob_data, y=ftrain[, phen],
                        method = ens_model, trControl = fitControl, metric='ROC')
        preds_class = predict(ens_fit)
        preds_probs = predict(ens_fit, type='prob')
        dat = cbind(data.frame(obs = ftrain[, phen],
                    pred = preds_class), preds_probs)
        res_train = twoClassSummary(dat, lev=colnames(preds_probs))

        # testing
        for (dom in names(domains)) {
            eval(parse(text=sprintf('var_names = colnames(%s_fit$trainingData)',
                                    dom)))
            # remove .outcome
            var_names = var_names[1:(length(var_names)-1)]
            numNAvars = rowSums(is.na(ftest[, var_names]))
            keep_me = numNAvars == 0
            this_data = ftest[keep_me, var_names]
            eval(parse(text=sprintf('%s_test_preds = data.frame(g1=rep(NA,
                                                                       nrow(ftest)),
                                                                g2=rep(NA,
                                                                        nrow(ftest)))',
                                    dom)))
            eval(parse(text=sprintf('preds = predict(%s_fit, type="prob", newdata=this_data)', dom)))
            # eval(parse(text=sprintf('print(varImp(%s_fit))', dom)))
            eval(parse(text=sprintf('%s_test_preds[keep_me, ] = preds', dom)))
        }
        preds_str = sapply(names(domains), function(d) sprintf('%s_test_preds[, 1]', d))
        cbind_str = paste('prob_test_data = cbind(',
                          paste(preds_str, collapse=','), ')',
                          sep="")
        eval(parse(text=cbind_str))
        colnames(prob_test_data) = names(domains)

        preds_class = predict(ens_fit, newdata=prob_test_data)
        preds_probs = predict(ens_fit, newdata=prob_test_data, type='prob')
        dat = cbind(data.frame(obs = ftest[, phen],
                        pred = preds_class), preds_probs)
        res = twoClassSummary(dat, lev=colnames(preds_probs))
        results[[fold_name]] = res
    }
}

# print(varImp(ens_fit))
mean_res = apply(as.data.frame(results), 1, mean)
sd_res = apply(as.data.frame(results), 1, sd)

line=sprintf("%s,%s,%s,%d,%s,%s,%d,%f,%f", my_sx, clf_model, ens_model,
             clin_diff, use_clin, use_meds,
             length(levels(data2[,phen])), mean_res['ROC'], sd_res['ROC'])
print(line)
write(line, file=out_file, append=TRUE)
