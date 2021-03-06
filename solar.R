library(nlme)

fname = '~/data/solar_paper/dti_mean_phenotype_cleanedWithinTract3sd_adhd_nodups_familyAndADHDSiblings.csv'
out_fname = '~/data/solar_paper/linear_dti_mean_3sd_familyAndADHDSiblings.csv'
p_thresh = .05

data = read.csv(fname)
# all variables to use as phenotype
phen_vars = 11:dim(data)[2]

# which subjects to use
idx = 1:dim(data)[1]
sxs = c('inatt', 'hi', 'total')

# setting up output dataframe
df = data.frame(tracts=colnames(data[,phen_vars]))

for (s in sxs) { 
    ps = vector()
    ts = vector()
    bs = vector()
    for (v in phen_vars) {
        y=data[,v]
        eval(parse(text=sprintf('sx=data$%s', s)))
        fit = lme(scale(y) ~ scale(sx) + sex + scale(age), random=~1|famid, data=data, na.action=na.omit)
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