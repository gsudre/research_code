library(nlme)

gf_fname = sprintf('~/data/solar_paper_v2/fmri_3min_melodicMasked_5comps.csv')
data_fname = sprintf('~/data/solar_paper_v2/nifti/ic00_validatedMean.1D')
subjs = sprintf('~/data/fmri_example11_all/3min.txt')
p_thresh = .1

cat('Loading data\n')
brain = read.table(data_fname)
gf = read.csv(gf_fname)
subjs = read.table(subjs)
brain = cbind(subjs, brain)
colnames(brain) = c('maskid', 'voxelMean')
data = merge(gf, brain, by='maskid')

# all variables to use as phenotype
phen_vars = dim(data)[2]

# which subjects to use
idx = 1:dim(data)[1]
sxs = c('inatt', 'HI', 'total', 'DX', 'DX_inatt', 'DX_hi', 'DX_comb')

print(data_fname)
for (s in sxs) {
    y = data[, phen_vars]
    eval(parse(text=sprintf('sx=data$%s', s)))
    # fm = as.formula("y ~ sx + sex*mean_enorm*age + sex*age*I(mean_enorm^2) + sex*mean_enorm*I(age^2) + sex*I(mean_enorm^2)*I(age^2)")
    fm = as.formula("y ~ sx + sex + mean_enorm + I(mean_enorm^2) + age + I(age^2)")
    fit = lme(fm, random=~1|famid, data=data, na.action=na.omit, method="ML")
    # # selecting which covariates to use
    # fm = "y ~ sx"
    # for (r in 3:dim(summary(fit)$tTable)[1]) {
    #     if (summary(fit)$tTable[r, 5] < p_thresh) {
    #         cname = rownames(summary(fit)$tTable)[r]
    #         cname = gsub("sexMale", "sex", cname)
    #         fm = sprintf('%s + %s', fm, cname)
    #     }
    # }
    # opt_fit = lme(as.formula(fm), random=~1|famid, data=data, na.action=na.omit, method="ML")
    opt_fit = fit
    p = summary(opt_fit)$tTable[2,5]
    t = summary(opt_fit)$tTable[2,4]
    b = summary(opt_fit)$tTable[2,1]

    cat(p, '\n')
    if (p < p_thresh) {
        cat(sprintf('===== %s =====\n', s))
        print(summary(opt_fit))
    }
}
