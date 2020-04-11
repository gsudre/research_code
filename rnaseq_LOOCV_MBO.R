args <- commandArgs(trailingOnly = TRUE)

if (length(args) > 0) {
    myregion = args[1]
    ncores = as.numeric(args[2])
    metric = args[3]
    out_file = args[4]
} else {
    myregion = 'Caudate'
    ncores = 2
    metric = 'auc'
    out_file = '/dev/null'
}

just_target = readRDS('~/data/rnaseq_derek/data_from_philip.rds')
if (myregion == 'both') {
    fname = '~/data/rnaseq_derek/X_noPH_zv_nzv_center_scale.rds'
    y = just_target[, 'Diagnosis']
} else {
    fname = sprintf('~/data/rnaseq_derek/X_%snoPH_zv_nzv_center_scale.rds',
                    myregion)
    y = just_target[, 'Diagnosis']
    y = just_target[just_target$Region==myregion, 'Diagnosis']
}

X = readRDS(fname)

library(caret)
library(xgboost)

library(mlrMBO)

myseed = 42
nfolds = 5

# bw
niters = 20 # to run in MBO
init_design = 50 # number of starting parameter combinations
nrounds = 400  # for xgb.cv
nstop = 10  # for xgb.cv

control = makeMBOControl()
control = setMBOControlTermination(control, iters = niters)

set.seed(myseed)
my_params = makeParamSet(
        makeNumericParam("eta",              lower = 0.001, upper = 0.5),
        makeNumericParam("gamma",            lower = 0,     upper = 7),
        makeIntegerParam("max_depth",        lower= 1,      upper = 5),
        makeIntegerParam("min_child_weight", lower= 1,      upper = 6),
        makeNumericParam("subsample",        lower = 0.4,   upper = 1),
        makeNumericParam("colsample_bytree", lower = 0.4,   upper = 1),
        makeNumericParam("lambda", lower = 1,   upper = 10),
        makeNumericParam("alpha", lower = 0,   upper = 3)
      )
des = generateDesign(n=init_design, par.set = my_params)

if (metric == 'auc') {
    eval_str = 'cv$evaluation_log[, max(test_auc_mean)]'
    do_minimize = FALSE
} else {
    eval_str = 'cv$evaluation_log[, min(test_error_mean)]'
    do_minimize = TRUE
}

y_probs = c()
best_params = c()
for (test_row in 1:nrow(X)) {
    train_rows = setdiff(1:nrow(X), test_row)
    X_train <- X[train_rows, ]
    X_test <- X[-train_rows, ]
    y_train <- y[train_rows]
    y_test <- y[-train_rows]

    print(sprintf('LOOCV %d / %d', test_row, nrow(X)))
    set.seed(myseed)
    cv_folds = createFolds(y_train, k = nfolds)

    dtrain <- xgb.DMatrix(data = as.matrix(X_train),
                          label = as.numeric(y_train)-1, missing=NA)
    dtest <- xgb.DMatrix(data = as.matrix(X_test),
                         label = as.numeric(y_test)-1, missing=NA)

    obj.fun  <- smoof::makeSingleObjectiveFunction(
    name = "xgb_cv_bayes",
    fn =   function(x){
      set.seed(myseed)
      cv <- xgb.cv(params = list(
                                booster          = "gbtree",
                                eta              = x["eta"],
                                max_depth        = x["max_depth"],
                                min_child_weight = x["min_child_weight"],
                                gamma            = x["gamma"],
                                subsample        = x["subsample"],
                                colsample_bytree = x["colsample_bytree"],
                                lambda = x["lambda"],
                                alpha = x["alpha"],
                                objective        = 'binary:logistic',
                                eval_metric     = metric),
                                data = dtrain,
                                nround = nrounds,
                                folds=  cv_folds,
                                prediction = FALSE,
                                showsd = TRUE,
                                early_stopping_rounds = nstop,
                                verbose = 0,
                                nthread=ncores)
        eval(parse(text=eval_str))
      },
      par.set = my_params,
      minimize = do_minimize
    )

    run = mbo(fun = obj.fun,
              design = des,
              control = control,
              show.info = TRUE)

    # another CV to determine nrounds
    set.seed(myseed)
    full_params = append(run$x, list(booster = "gbtree",
                                     objective = 'binary:logistic',
                                     eval_metric = metric))
    cv <- xgb.cv(params = full_params,
                data = dtrain,
                nround = nrounds,
                folds=  cv_folds,
                prediction = FALSE,
                showsd = TRUE,
                early_stopping_rounds = nstop,
                verbose = 0,
                nthread=ncores)

    # train final model for this hold out
    set.seed(myseed)
    xg_mod <- xgboost(data = dtrain, params = full_params,
                      nround = cv$best_iteration,
                      verbose = F, nthread=ncores)

    y_probs = c(y_probs, predict(xg_mod, dtest))
    tmp = data.frame(run$x, y=run$y)
    best_params = rbind(best_params, tmp)
    print(best_params)

    # updated LOOCV predictions
    y_preds = factor(ifelse (y_probs > 0.5, levels(y)[2], levels(y)[1]),
                     levels=levels(y))
    dat = data.frame(obs = y[1:length(y_probs)], pred = y_preds, junk=y_probs)
    colnames(dat)[3] = levels(y)[2]
    print(twoClassSummary(dat, lev=levels(y)))
}

save(best_params, myseed, fname, nfolds, my_params, dat, niters, init_design,
     nrounds, nstop, metric, file=out_file)
