library(nlme)
library(MASS)

fname = '~/data/solar_paper_review/fmri_nets_mean_heritable.csv'
out_fname = '~/data/solar_paper_review/linear_fmri_nets_mean_heritable.csv'
p_thresh = .05

data = read.csv(fname)
# all variables to use as phenotype
phen_vars = which(grepl("net", names(data)))

# which subjects to use
idx = 1:dim(data)[1]
sxs = c('inatt', 'HI', 'total', 'DX', 'DX_inatt', 'DX_hi', 'DX_comb',
        'DX_inatt_noComb', 'DX_hi_noComb')

# setting up output dataframe
df = data.frame(tracts=colnames(data[,phen_vars]))

print(fname)
for (s in sxs) {
    ps = vector()
    ts = vector()
    bs = vector()
    for (v in phen_vars) {
        y = data[,v]
        eval(parse(text=sprintf('sx=data$%s', s)))
        fm = as.formula("y ~ sx + sex + mean_enorm + I(mean_enorm^2) + age + I(age^2)")
        fit = lme(fm, random=~1|famid, data=data, na.action=na.omit, method="ML")
        # selecting which covariates to use
        fm = "y ~ sx"
        for (r in 3:dim(summary(fit)$tTable)[1]) {
            if (summary(fit)$tTable[r, 5] < .1) {
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
    print(sprintf('==== Results for %s ====', s))
    good_ps = which(ps <= p_thresh)
    print(sprintf("Found %d/%d good tests (%.3f)",length(good_ps),length(ps),p_thresh))
    for (p in good_ps) {
        print(sprintf('%s: p=%.3f, t=%.3f',colnames(data)[phen_vars[p]],ps[p],ts[p]))
    }
    bf_thresh = p_thresh / length(ps)
    good_ps = which(ps <= bf_thresh)
    print(sprintf("Found %d/%d good tests (%.3f, Bonferroni)",length(good_ps),length(ps),bf_thresh))
    for (p in good_ps) {
        print(sprintf('%s: p=%.3f, t=%.3f',colnames(data)[phen_vars[p]],ps[p],ts[p]))
    }
    eval(parse(text=sprintf('df$%s_ts=ts', s)))
    eval(parse(text=sprintf('df$%s_ps=ps', s)))
    eval(parse(text=sprintf('df$%s_bs=bs', s)))
}
# to export the results
write.csv(df,file=out_fname,row.names=F)
