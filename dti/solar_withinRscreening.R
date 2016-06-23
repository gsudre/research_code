library(nlme)
library(MASS)

fname = '~/data/solar_paper_v2/dti_mean_phenotype_cleanedWithinTract3sd_adhd_nodups_extendedAndNuclear_mvmt_pctMissingSE10_FAbt2.5_whites.csv'
out_fname = '~/data/solar_paper_v2/linear_dti_mean_phenotype_cleanedWithinTract3sd_adhd_nodups_extendedAndNuclear_mvmt_pctMissingSE10_FAbt2.5_additive_whites.csv'
# out_fname = '~/data/solar_paper_v2/tmp.csv'
>>>>>>> 4141146cbe480879d2da52c21d4e1abfd712bac5
p_thresh = .05

data = read.csv(fname)
# all variables to use as phenotype
phen_vars = c(which(grepl("left", names(data))), which(grepl("right", names(data))), which(grepl("cc", names(data))))
# phen_vars = c('rd_left_ifo')

# which subjects to use
idx = 1:dim(data)[1]
sxs = c('inatt', 'hi', 'total')#, 'DX', 'DX_inatt', 'DX_hi', 'DX_comb')

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
        # fm = as.formula("y ~ sx + sex*mvmt*age + sex*age*I(mvmt^2) + sex*mvmt*I(age^2) + sex*I(mvmt^2)*I(age^2)")
        fm = as.formula("y ~ sx + sex + mvmt + I(mvmt^2) + age + I(age^2)")
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
