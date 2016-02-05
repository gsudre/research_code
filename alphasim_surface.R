# Script to run Bartholt's models with permuted data
load('~/research_code/mni_functions.RData')
library('nlme')

args <- commandArgs(trailingOnly = TRUE)
var = args[1]
t_str = args[2]
perm = as.numeric(args[3])
surf = args[4]
fwhm = as.numeric(args[5])

# var = 'ra'
# t_str = 'ordered'
# perm = 1
# surf = '~/data/bartholt/new_right_amygdala.asc'
# fwhm = 5

out_dir = '~/data/bartholt/perms/'
fname = '~/data/bartholt/EMOT_OCT_16.RData'
load(fname)

# reset random seed
set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )

eval(parse(text=sprintf('data=dt_%s_baseline', var)))
# index it
fm = 'y~GROUP4_ordered+age_cent+sex+scantype'

# generate random data in the same dimensions as the actual data
ncols = dim(data)[1]
nrows = dim(data)[2]
rdata = matrix(runif(ncols * nrows), ncol=ncols)
fout = sprintf('%s/%s_%s_%d_raw.asc', out_dir, var, t_str, perm)
write.table(t(rdata), fout, row.names=F, col.names=F) 

# smooth it in AFNI
sm_fout = sprintf('%s/smooth_%s_%s_%d', out_dir, var, t_str, perm)
cmd_str = sprintf('SurfSmooth -i_fs %s -input %s -met HEAT_07 -target_fwhm %f -output %s', surf, fout, fwhm, sm_fout)
system(cmd_str)

# read back the smoothed data
sm_fin = sprintf('%s/smooth_%s_%s_%d.1D.dset', out_dir, var, t_str, perm)
sm_rdata = as.matrix(read.table(sm_fin))

# cleaning up after ourselves right away to free up memory
cmd_str = sprintf('rm %s/smooth_%s_%s_%d.1D.dset %s/smooth_%s_%s_%d.1D.smrec %s', out_dir, var, t_str, perm, out_dir, var, t_str, perm, fout)
system(cmd_str)

# run model with simulated and smoothed data
fit = mni.vertex.mixed.model(gf_baseline, fm, ~1|famid1, sm_rdata)
res = fit$t.value[, 'GROUP4_ordered.L']

res[is.na(res)] = 0

# spit out the results and cleaning up after ourselves
fout = sprintf('%s/%s_%s_%d.asc', out_dir, var, t_str, perm)
write.table(res, fout, row.names=F, col.names=F) 
