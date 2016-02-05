# Script to run Bartholt's models with permuted data
load('~/research_code/mni_functions.RData')
library('nlme')

args <- commandArgs(trailingOnly = TRUE)
var = args[1]
t_str = args[2]
perm = as.numeric(args[3])
# var = 'rh'
# perm = 1

fname = sprintf('~/data/bartholt/dt_%s.RData', var)
load(fname)
eval(parse(text=sprintf('data=dt_%s', var)))
eval(parse(text=sprintf('gf=gf_%s', var)))
# index it
fm = 'y~dpscl_tscore+fsiq+dx+scantype+age_scan+sex'
idx = gf$cbcl_used==1
gf = gf[idx, ]
data = data[, idx]

# scramble one of the sides of the equation
n = dim(data)[2]
perm_labels <- sample.int(n, replace = FALSE)
perm_data <- data[, perm_labels]

# run model with scrambled data
# fit = mni.vertex.statistics(gf, fm, perm_data)
# res = fit$tstatistic[, 2]
fit = mni.vertex.mixed.model(gf, fm, ~1|famid1, perm_data)
res = fit$t.value[, 2]

res[is.na(res)] = 0

# spit out the results
fout = sprintf('~/data/bartholt/perms/%s_%s_%d.asc', var, t_str, perm)
write.table(res, fout, row.names=F, col.names=F) 