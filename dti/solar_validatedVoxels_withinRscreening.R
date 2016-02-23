library(nlme)

group = 'mean'
net = 'rd'
gf_fname = sprintf('~/data/solar_paper_v2/dti_%s_phenotype_cleanedWithinTract3sd_adhd_nodups_extendedAndNuclear_mvmt_pctMissingSE10_FAbt2.5.csv', group)
data_fname = sprintf('~/data/solar_paper_v2/nifti/additive/dti_mean_%s_validated_NN1.txt', net)
subjs = '~/data/dti_voxelwise/subjs.txt'
p_thresh = .1

cat('Loading data\n')
brain = read.table(data_fname)
gf = read.csv(gf_fname)
subjs = read.table(subjs)
brain = cbind(subjs, t(brain))
data = merge(gf, brain, by.x='mask.id', by.y='V1')

# all variables to use as phenotype
phen_vars = (dim(gf)[2] + 1):dim(data)[2]

# which subjects to use
idx = 1:dim(data)[1]
sxs = c('inatt', 'hi', 'total', 'DX', 'DX_inatt', 'DX_hi', 'DX_comb')

df = data.frame(voxel=colnames(data[,phen_vars]))
for (s in sxs) {
    ps = vector()
    ts = vector()
    bs = vector()
    for (v in phen_vars) {
        cat(sprintf('%s: %s / %d\n', s, colnames(data)[v], length(phen_vars)))
        y = data[,v]
        eval(parse(text=sprintf('sx=data$%s', s)))
        # fm = as.formula("y ~ sx + sex*mean_enorm*age + sex*age*I(mean_enorm^2) + sex*mean_enorm*I(age^2) + sex*I(mean_enorm^2)*I(age^2)")
        fm = as.formula("y ~ sx + sex + mvmt + I(mvmt^2) + age + I(age^2)")
        fit = try(lme(fm, random=~1|famid, data=data, na.action=na.omit, method="ML"))
        if (length(fit) > 1) {
            # selecting which covariates to use
            fm = "y ~ sx"
            for (r in 3:dim(summary(fit)$tTable)[1]) {
                if (summary(fit)$tTable[r, 5] < p_thresh) {
                    cname = rownames(summary(fit)$tTable)[r]
                    cname = gsub("sexMale", "sex", cname)
                    fm = sprintf('%s + %s', fm, cname)
                }
            }
            opt_fit = try(lme(as.formula(fm), random=~1|famid, data=data, na.action=na.omit, method="ML"))
            if (length(opt_fit) > 1) {
                ps = c(ps, summary(opt_fit)$tTable[2,5])
                ts = c(ts, summary(opt_fit)$tTable[2,4])
                bs = c(bs, summary(opt_fit)$tTable[2,1])
                } else {
                    ps = c(ps, 1)
                    ts = c(ts, 0)
                    bs = c(bs, 0)
                }
        } else {
            ps = c(ps, 1)
            ts = c(ts, 0)
            bs = c(bs, 0)
        }
    }
    eval(parse(text=sprintf('df$%s_ts=ts', s)))
    eval(parse(text=sprintf('df$%s_ps=ps', s)))
    eval(parse(text=sprintf('df$%s_bs=bs', s)))
}
out_fname = sprintf('~/data/solar_paper_v2/linear_dti_mean_validated_%s_NN1_additive.csv', net)
write.csv(df,file=out_fname,row.names=F)

