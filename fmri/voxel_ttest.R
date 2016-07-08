library(nlme)
library(foreach)
library(doParallel)

group = '3min'
net = 0
gf_fname = '~/data/fmri/gf.csv'
data_fname = sprintf('~/data/fmri_full_grid/net%02d.txt', net)
out_root = '~/data/fmri_full_grid/results/net%02d_%s_additive'
nii_template = '~/data/fmri_full_grid/brain_mask_full.nii'
subjs = '~/data/fmri/joel_all.txt'
p_thresh = .1


ncores = max(1, detectCores() - 1)
cl<-makeCluster(ncores, outfile="")
registerDoParallel(cl)


cat('Loading data\n')
brain = read.table(data_fname)
gf = read.csv(gf_fname)
subjs = read.table(subjs)
brain = cbind(subjs, t(brain))
data = merge(gf, brain, by.x='maskid', by.y='V1')


# all variables to use as phenotype
phen_vars = (dim(gf)[2] + 1):dim(data)[2]

# which subjects to use
idx = 1:dim(data)[1]
sxs = c('inatt', 'hi', 'total')

nvoxels = length(phen_vars)

for (s in sxs) {
    df = data.frame(voxel=colnames(data[,phen_vars]))
    res = matrix(nrow=nvoxels, ncol=3, data=1)
    # foreach(v = 1:nvoxels) %dopar% {
    #     print(sprintf('%s: %s / %d\n', s, v, nvoxels))
    #     y = data[, phen_vars[v]]
    #     eval(parse(text=sprintf('sx=data$%s', s)))
    #     fm = as.formula("y ~ sx + sex + mvmt + I(mvmt^2) + age + I(age^2)")
    #     fit = lm(fm, data=data, na.action=na.omit)
    #     # selecting which covariates to use
    #     fm = "y ~ sx"
    #     for (r in 3:dim(summary(fit)$coefficient)[1]) {
    #         if (summary(fit)$coefficient[r, 4] < p_thresh) {
    #             cname = rownames(summary(fit)$coefficient)[r]
    #             cname = gsub("sexMale", "sex", cname)
    #             fm = sprintf('%s + %s', fm, cname)
    #         }
    #     }
    #     opt_fit = lm(as.formula(fm), data=data, na.action=na.omit)
    #     res[v, 1] = summary(opt_fit)$coefficient[2, 3]  # t-stat
    #     res[v, 2] = 1 - summary(opt_fit)$coefficient[2, 4]  # p-val
    # }
    # write out results and convert to .nii
    out_fname = sprintf(out_root, net, s)
    write.table(res, file=sprintf('%s.txt', out_fname),
                col.names=F, row.names=F)
    system(sprintf('cat %s.txt | 3dUndump -xyz -master %s -datum float -prefix %s.nii.gz -overwrite -', out_fname, nii_template, out_fname), wait=T)
}
stopCluster(cl)