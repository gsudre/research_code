library(nlme)
library(MASS)

fname = '~/data/solar_paper_review/fmri_nets_mean_heritable.csv'
out_fname = '~/data/solar_paper_review/ANOVA_fmri_nets_mean_heritable.csv'
p_thresh = .05

data = read.csv(fname)
# all variables to use as phenotype
phen_vars = which(grepl("net", names(data)))
group_var = 'DX2'

eval(parse(text=sprintf('sx=data$%s', group_var)))
groups = unique(sx)
ngroups = length(groups)

# setting up output dataframe
df = data.frame(tracts=colnames(data[,phen_vars]))

# phen_vars = 77

print(fname)
ps = vector()
Fs = vector()
for (v in phen_vars) {
    y = data[,v]
    fm = as.formula("y ~ sx + sex + mean_enorm + I(mean_enorm^2) + age + I(age^2)")
    # options(contrasts = c("contr.sum", "contr.poly"))
    options(contrasts = c("contr.treatment", "contr.poly"))
    fit = lme(fm, random=~1|famid, data=data, na.action=na.omit, method="ML")
    # selecting which covariates to use
    fm = "y ~ sx"
    # ignores the intercept plus (ngroups-1)
    start_at = 1 + (ngroups - 1) + 1
    for (r in start_at:dim(summary(fit)$tTable)[1]) {
        if (summary(fit)$tTable[r, 5] < .1) {
            cname = rownames(summary(fit)$tTable)[r]
            cname = gsub("sexMale", "sex", cname)
            fm = sprintf('%s + %s', fm, cname)
        }
    }
    opt_fit = lme(as.formula(fm), random=~1|famid, data=data, na.action=na.omit, method="ML")
    an_fit = anova(opt_fit)
    ps = c(ps, an_fit$"p-value"[2])
    Fs = c(Fs, an_fit$"F-value"[2])

    # spit out to the screen the pairwise posthoc t-tests if needed
    if (an_fit$"p-value"[2] < .05) {
        cat('\n\n', colnames(data)[v], '\n')
        pvals = array(NA, dim=c(ngroups, ngroups))
        colnames(pvals) = groups
        rownames(pvals) = groups
        tstats = pvals
        for (g in 1:ngroups) {
            sx = relevel(sx, ref=as.character(groups[g]))
            pw_fit = lme(as.formula(fm), random=~1|famid, data=data, na.action=na.omit, method="ML")
            # step over intercept
            for (r in 2:ngroups) {
                cname = rownames(summary(pw_fit)$tTable)[r]
                cname = gsub("sx", "", cname)
                cidx = which(groups == cname)
                if (cidx > 0) {
                    pvals[g, cidx] = summary(pw_fit)$tTable[r, 5]
                    tstats[g, cidx] = summary(pw_fit)$tTable[r, 4]
                }
            }
            # print(summary(pw_fit))
        }
        cat('P-VALUES\n')
        print(pvals)
        cat('T-STATS\n')
        print(tstats)
    }
}

df$ANOVA_F=Fs
df$ANOVA_pval=ps

# to export the results
write.csv(df,file=out_fname,row.names=F)
