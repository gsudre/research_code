# Script to run Bartholt's models with permuted data
load('~/research_code/mni_functions.RData')
library(nlme)

args <- commandArgs(trailingOnly = TRUE)
var = args[1]
t_str = args[2]
perm = as.numeric(args[3])
# var = 'rh'
# perm = 1
# t_str = 'tmp'

fname = sprintf('~/data/bartholt/dt_%s.RData', var)
load(fname)
eval(parse(text=sprintf('data=dt_%s', var)))
eval(parse(text=sprintf('gf=gf_%s', var)))
# index it
idx = gf$cbcl_used==1
gf = gf[idx, ]
data = data[, idx]

# before scrambling the data we need to calculate the residuals
resid = data
for (v in 1:dim(data)[2]) {
    fit = lm(data[v, ] ~ fsiq+dx+scantype+age_scan+sex, data=gf)
    resid[v, ] = residuals(fit)
}

# scramble one of the sides of the equation
n = dim(resid)[2]
perm_labels <- sample.int(n, replace = FALSE)
perm_data <- resid[, perm_labels]

# run model with scrambled data
# fit = mni.vertex.statistics(gf, 'y ~ dpscl_tscore', perm_data)
# res = fit$tstatistic[, 2]
fit = mni.vertex.mixed.model(gf, 'y ~ dpscl_tscore', ~1|famid1, perm_data)
res = fit$t.value[, 2]

res[is.na(res)] = 0

# spit out the results
fout = sprintf('~/data/bartholt/perms/%s_%s_%d.asc', var, t_str, perm)
write.table(res, fout, row.names=F, col.names=F) 