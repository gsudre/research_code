args <- commandArgs(trailingOnly = TRUE)

if (length(args) > 0) {
    myseed = as.numeric(args[1])
    WNH = as.logical(args[2])
    nboot = as.numeric(args[3])
    mytest = args[4]
} else {
    myseed = 42
    WNH = T
    nboot = 1000
    mytest = 'ttest'
}

library(doParallel)
ncores = as.numeric(Sys.getenv('SLURM_CPUS_PER_TASK'))
cl = makeCluster(ncores)

data = readRDS('~/data/rnaseq_derek/data_from_philip_POP_and_PCs.rds')
data = data[data$Region=='ACC',]
if (WNH) {
    imWNH = data$C1 > 0 & data$C2 < -.075
    data = data[which(imWNH),]
}

covar_names = c(# brain-related
                "bainbank", 'PMI', 'Manner.of.Death',
                # technical
                'batch', 'RINe',
                # clinical
                'comorbid_group', 'substance_group',
                # others
                'Sex', 'Age')

# only covariates can be binary, and I'm getting stack overflow errors sending
# everything to dummyvars...
data2 = data[, c(covar_names, 'Diagnosis')]
library(caret)
dummies = dummyVars(Diagnosis ~ ., data = data2)
data3 = predict(dummies, newdata = data2)
# remove linear combination variables
comboInfo <- findLinearCombos(data3)
data3 = data3[, -comboInfo$remove]

print('Removing weird variables...')
# remove weird variables
grex_names = colnames(data)[grepl(colnames(data), pattern='^grex')]
pp = preProcess(data[, grex_names], method=c('zv', 'nzv', 'range'),
                rangeBounds=c(0,1))
a = predict(pp, data[, grex_names])
n0 = colSums(a==0)
imbad = names(n0)[n0>1]
good_grex = grex_names[!(grex_names %in% imbad)]

data4 = cbind(data[, good_grex], data3)

print('Data preprocessing...')
set.seed(myseed)
# data4 doesn't even have Diagnosis, and no NAs
pp_order = c('zv', 'nzv', 'center', 'scale')
pp = preProcess(data4, method = pp_order)
X = predict(pp, data4)
y = data2$Diagnosis

print('Data normalizing...')
grex_only = colnames(X)[grepl(colnames(X), pattern='^grex')]
library(bestNormalize)
Xgrex = X[, grex_only]
for (v in 1:ncol(Xgrex)) {
    bn = orderNorm(Xgrex[, v])
    Xgrex[, v] = bn$x.t
}
pp_order = c('center', 'scale')
pp = preProcess(Xgrex, method = pp_order)
Xgrex = predict(pp, Xgrex)

print('Creating Xrand...')
set.seed(myseed)
Xrand = Xgrex
for (v in 1:ncol(Xrand)) {
    Xrand[, v] = rnorm(nrow(Xrand))
}
print('Starting bootstrap...')
fscores = matrix(nrow=nboot, ncol=ncol(Xrand))
set.seed(myseed)
for (b in 1:nboot) {
    print(sprintf('boot %d', b))
    idx = sample(1:nrow(Xrand), nrow(Xrand), replace=T)
    X_train = Xrand[idx, ]
    y_train = y[idx]

    clusterExport(cl, c("X_train", 'y_train'))
    if (mytest == 'wilcox') {
        ps = parSapply(cl, 1:ncol(Xrand),
                       function(v) wilcox.test(X_train[y_train=='Case', v],
                                                   X_train[y_train=='Control', v]
                                                   )$p.value)
    } else {
        ps = parSapply(cl, 1:ncol(Xrand),
                       function(v) t.test(X_train[y_train=='Case', v],
                                                    X_train[y_train=='Control', v],
                                                    var.pool=T,
                                                    )$p.value)
    }
    fscores[b, ] = ps
}
fout = sprintf('~/data/rnaseq_derek/perms/rnd_%s_%s_1000boot_p%06d.rds',
               mytest, WNH, myseed)
saveRDS(fscores, file=fout, compress=T)

