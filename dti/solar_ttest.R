library(nlme)

fname = '~/data/solar_paper_v2/dti_max_phenotype_cleanedWithinTract3sd_adhd_nodups_extendedAndNuclear_mvmt_pctMissingSE10_FAbt2.5.csv'
out_fname = '~/data/solar_paper_v2/categoric_dti_max_phenotype_cleanedWithinTract3sd_adhd_nodups_extendedAndNuclear_mvmt_pctMissingSE10_FAbt2.5.csv'
p_thresh = .05

data = read.csv(fname)
# all variables to use as phenotype
phen_vars = c(which(grepl("left", names(data))), which(grepl("right", names(data))), which(grepl("cc", names(data))))

# which subjects to use
idx = 1:dim(data)[1]
inatt = data$inatt
hi = data$hi
total = inatt + hi

# setting up output dataframe
df = data.frame(tracts=colnames(data[,phen_vars]))

print(fname)
ps = vector()
ts = vector()
bs = vector()
for (v in phen_vars) {
    y=data[,v]
    fit = lme(y ~ DX + sex + age + mvmt, random=~1|famid, data=data, na.action=na.omit)
    ps = c(ps, summary(fit)$tTable[2,5])
    ts = c(ts, summary(fit)$tTable[2,4])
    bs = c(bs, summary(fit)$tTable[2,1])
}
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

# to export the results
write.csv(df,file=out_fname,row.names=F)