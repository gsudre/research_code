library(nlme)

fname = '~/data/solar_paper_v2/fmri_3min_melodicMasked_5comps_nuclear.csv'
out_fname = '~/data/solar_paper_v2/linear_fmri_3min_melodicMasked_5comps_enorm12_nuclear.csv'
p_thresh = .05

data = read.csv(fname)
# all variables to use as phenotype
phen_vars = which(grepl("net", names(data)))

# which subjects to use
idx = 1:dim(data)[1]
sxs = c('inatt', 'HI', 'total', 'DX', 'DX_inatt', 'DX_hi', 'DX_comb')

# setting up output dataframe
df = data.frame(tracts=colnames(data[,phen_vars]))

print(fname)
for (s in sxs) { 
    ps = vector()
    ts = vector()
    bs = vector()
    for (v in phen_vars) {
        y=data[,v]
        eval(parse(text=sprintf('sx=data$%s', s)))
        # fit = lme(scale(y) ~ scale(sx) + sex + scale(age), random=~1|famid, data=data, na.action=na.omit)
        fit = lme(y ~ sx + sex + age + mean_enorm + I(age^2) + I(mean_enorm^2), random=~1|famid, data=data, na.action=na.omit)
        ps = c(ps, summary(fit)$tTable[2,5])
        ts = c(ts, summary(fit)$tTable[2,4])
        bs = c(bs, summary(fit)$tTable[2,1])
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