fname = '~/Downloads/gf_impute_based_anatomy_272.csv'
my_sx = 'inatt  '
reg_model = 'dummy'
nfolds = 3
nreps = 9999
out_file = '/dev/null'
# metrics to evaluate
r2_eval = 0.074217
rmse_eval = 0.575755

library(caret)
data = read.csv(fname)
# so they don't get rescaled
if (grepl(x=fname, pattern='anat')) {
    data$sex_numeric = as.factor(data$sex_numeric)
    data$SES_group3 = as.factor(data$SES_group3)
    var_names = colnames(data)[c(10:17, 18:29, 30:34, 4:6)]
    phen = sprintf("slope_%s_res_trim.x", my_sx)
} else {
    data$sex_numeric = as.factor(data$sex_numeric)
    data$SES_group3_165 = as.factor(data$SES_group3_165)
    var_names = colnames(data)[c(21:28, 29:40, 41:45, 5:6, 95, 9:20)]
    phen = sprintf("slope_%s_res_trim", my_sx)
}


set.seed(42)
ctl = createMultiFolds(data[, phen], k=nfolds, times=nreps)

results = c()
for (rep in 1:nreps) {
    preds = c()
    actual = c()
    if (nreps >= 1000) {
        rep_name = sprintf('Rep%04d', rep)
    } else if (nreps >= 100) {
        rep_name = sprintf('Rep%03d', rep)
    } else if (nreps >= 10) {
        rep_name = sprintf('Rep%02d', rep)
    } else {
        rep_name = sprintf('Rep%d', rep)
    }
    # print(rep_name)
    for (fold in 1:nfolds) {
        if (nfolds >= 10) {
            fold_name = sprintf('Fold%02d', fold)
        } else {
            fold_name = sprintf('Fold%d', fold)
        }
        fold_name = sprintf('%s.%s', fold_name, rep_name)

        fold_rows = ctl[[fold_name]]
        ftrain = data[fold_rows,]
        ftest = data[-fold_rows,]
        preds = c(preds, rep(mean(ftrain[, phen]), nrow(ftest)))
        actual = c(actual, ftest[, phen])
    }
    results = rbind(results, postResample(actual, preds))
}
line=sprintf("%s,%s,%s,%d,%d,%f,%f", my_sx, reg_model, fname,
             nfolds, nreps, mean(results[,'Rsquared']), sd(results[,'Rsquared']))
print(line)
line=sprintf("%s,%s,%s,%d,%d,%f,%f", my_sx, reg_model, fname,
             nfolds, nreps, mean(results[,'RMSE']), sd(results[,'RMSE']))
print(line)

print(sprintf('R2 = %f, p = %f',
              r2_eval, sum(results[,'Rsquared'] > r2_eval)/nreps))
print(sprintf('RMSE = %f, p = %f',
              rmse_eval, sum(results[,'RMSE'] < rmse_eval)/nreps))

par(mfrow=c(1, 2))
hist(results[,'Rsquared'], breaks=50, main=sprintf('R2_%s_%d', my_sx, nrow(data)))
hist(results[,'RMSE'], breaks=50, main=sprintf('RMSE_%s_%d', my_sx, nrow(data)))

