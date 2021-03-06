library(nlme)

net = 6
gf_fname = '~/data/solar_paper_review/fmri_nets_mean_heritable.csv'
data_fname = sprintf('~/data/solar_paper_review/net%02d_validated_NN1.txt', net)
subjs = '~/data/solar_paper_review/3min.txt'
out_fname = sprintf('~/data/solar_paper_review/linear_fmri_net%02d_validated.csv', net)
p_thresh = .1

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
sxs = c('inatt', 'HI', 'total', 'DX', 'DX_inatt', 'DX_hi', 'DX_comb',
        'DX_inatt_noComb', 'DX_hi_noComb')

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
        fm = as.formula("y ~ sx + sex + mean_enorm + I(mean_enorm^2) + age + I(age^2)")
        fit = lme(fm, random=~1|famid, data=data, na.action=na.omit, method="ML")
        # selecting which covariates to use
        fm = "y ~ sx"
        for (r in 3:dim(summary(fit)$tTable)[1]) {
            if (summary(fit)$tTable[r, 5] < p_thresh) {
                cname = rownames(summary(fit)$tTable)[r]
                cname = gsub("sexMale", "sex", cname)
                fm = sprintf('%s + %s', fm, cname)
            }
        }
        opt_fit = lme(as.formula(fm), random=~1|famid, data=data, na.action=na.omit, method="ML")
        ps = c(ps, summary(opt_fit)$tTable[2,5])
        ts = c(ts, summary(opt_fit)$tTable[2,4])
        bs = c(bs, summary(opt_fit)$tTable[2,1])
    }
    eval(parse(text=sprintf('df$%s_ts=ts', s)))
    eval(parse(text=sprintf('df$%s_ps=ps', s)))
    eval(parse(text=sprintf('df$%s_bs=bs', s)))
}
write.csv(df,file=out_fname,row.names=F)

