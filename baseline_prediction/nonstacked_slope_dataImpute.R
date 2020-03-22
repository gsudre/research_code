args <- commandArgs(trailingOnly = TRUE)

if (length(args) > 0) {
    fname = args[1]
    my_sx = args[2]
    reg_model = args[3]
    nfolds = as.numeric(args[4])
    nreps = as.numeric(args[5])
    out_file = args[6]
} else {
    fname = '~/data/baseline_prediction/prs_start/gf_impute_based_dti_165.csv'
    my_sx = 'hi'
    reg_model = 'blassoAveraged'
    nfolds = 10
    nreps = 10
    out_file = '/dev/null'
}

library(caret)
data = read.csv(fname)
# so they don't get rescaled
if (grepl(x=fname, pattern='anat')) {
    mymod = 'anat'
    data$sex_numeric = as.factor(data$sex_numeric)
    data$SES_group3 = as.factor(data$SES_group3)
    var_names = colnames(data)[c(10:17, 18:29, 30:34, 4:6)]
    phen = sprintf("slope_%s_res_trim.x", my_sx)
} else {
    mymod = 'dti'
    data$sex_numeric = as.factor(data$sex_numeric)
    data$SES_group3_165 = as.factor(data$SES_group3_165)
    var_names = colnames(data)[c(21:28, 29:40, 41:45, 5:6, 95, 9:20)]
    phen = sprintf("slope_%s_res_trim", my_sx)
}


set.seed(42)
fitControl <- trainControl(method = "repeatedcv",
                           number = nfolds,
                           repeats = nreps)

# if imputation is fair game before we split, so is scaling
scale_me = c()
for (v in var_names) {
    if (!is.factor(data[, v])) {
        scale_me = c(scale_me, v)
    } else {
        data[, v] = as.numeric(data[, v])
    }
}
data[, scale_me] = scale(data[, scale_me])

set.seed(42)
fit <- train(x=data[, var_names],
             y=data[, phen],
             method = reg_model,
             trControl = fitControl,
             tuneLength = 10)

print(varImp(fit))

print(fit)

line=sprintf("%s,%s,%s,%d,%d,%f,%f", my_sx, reg_model, mymod,
             nfolds, nreps, mean(fit$results$RMSE), sd(fit$results$RMSE))
print(line)
write(line, file=out_file, append=TRUE)

# export variable importance
a = varImp(fit, useModel=T)
b = varImp(fit, useModel=F)
fname = sprintf('~/data/baseline_prediction/prs_start/%s_%s_%s.csv', reg_model,
                mymod, my_sx)
write.csv(cbind(a$importance, b$importance), file=fname)

# export variable importance
fname = sprintf('~/data/baseline_prediction/prs_start/fit_%s_%s_%s.Rdata', reg_model,
                mymod, my_sx)
save(fit, file=fname)