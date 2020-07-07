args <- commandArgs(trailingOnly = TRUE)
if (length(args) > 1) {
    methyl_fname = args[1]
    ncpu = as.numeric(args[2])
    out_fname = args[3]
} else {
    methyl_fname = ''
    ncpu = 2
    out_fname = '~/tmp/temp1.csv'
}


a = readRDS('~/data/longitudinal_methylome/UPDATED320.rds')

# a = a[a$sample_type=='Saliva',]

tmp = a$ageACQ
for (s in unique(a$PersonID)) {
    subj_rows = which(a$PersonID==s)
    if (a[subj_rows[1], 'ageACQ'] < a[subj_rows[2], 'ageACQ']) {
        tmp[subj_rows] = c(1, 2)
    } else {
        tmp[subj_rows] = c(2, 1)
    }
}
a = cbind(a, tmp)
f = read.csv('~/data/longitudinal_methylome/ROC_data_pheno_file_yun_ching_used.csv')

fit_wrapper = function(x) {
    a_slim = a[, c('PersonID', 'tmp', x)]
    a_wide = reshape(a_slim, idvar = "PersonID",
                     timevar = "tmp",
                     direction = "wide")
    m = merge(a_wide, f, by='PersonID')
    f_str = '%s.2 ~ %s.1 + sample_type + age.diff + ageACQ.1 + PC1 + PC2 + PC3 + PC4 + PC5 + SV.one.m2 + CD8T.diff + CD4T.diff + NK.diff + Bcell.diff + Mono.diff + Gran.diff + sex'
    fit = lm(as.formula(sprintf(f_str, x, x)), data=m)
    res = summary(fit)$coefficients
    myrow = which(grepl(rownames(res), pattern=sprintf('^%s', x)))
    # myrow = which(grepl(rownames(res), pattern=sprintf('^%s.1:sample', x)))
    return(res[myrow, ])
}

if (length(methyl_fname) < 5) {
    Ms = colnames(a)[grepl(colnames(a), pattern='^cg')][1:10]
} else {
    Ms = read.table(methyl_fname)[, 1]
}

library(parallel)
cl <- makeCluster(ncpu, type='FORK')
m1_res = parLapply(cl, Ms, fit_wrapper)
all_res = do.call(rbind, m1_res)
rownames(all_res) = Ms


write.csv(all_res, file=out_fname, quote=F)
stopCluster(cl)
