# spits out the BIC of different models
library(nlme)
library(MASS)

fname = '~/data/solar_paper_review/fmri_netMask_mean_GE22.csv'
out_fname = '~/data/solar_paper_review/BIC_fmri_GE22.csv'
p_thresh = .05

data = read.csv(fname)
# all variables to use as phenotype
# phen_vars = c(which(grepl("left", names(data))), which(grepl("right", names(data))), which(grepl("cc", names(data))))
phen_vars = which(grepl("net0", names(data)))

# which subjects to use
idx = 1:dim(data)[1]

terms = c('age', 'I(age^2)', 'age_squaredModel')
res = matrix(nrow=length(phen_vars), ncol=(4*length(terms) + 3))
cnames = vector()
for (t in terms) {
    cnames = c(cnames, sprintf('%s_beta', t))
    cnames = c(cnames, sprintf('%s_se', t))
    cnames = c(cnames, sprintf('%s_tstat', t))
    cnames = c(cnames, sprintf('%s_pval', t))
}
colnames(res) = c('BIC_constant', 'BIC_linear', 'BIC_quad', cnames)

print(fname)
cnt = 1
for (v in phen_vars) {
    y = data[,v]
    const = "y ~ 1"
    lin = "y ~ age"
    quad = "y ~ age + I(age^2)"
    fit = lme(as.formula(const), data=data, random=~1|famid, na.action=na.omit)
    res[cnt, 1] = BIC(fit)
    fit = lme(as.formula(lin), data=data, random=~1|famid, na.action=na.omit)
    res[cnt, 2] = BIC(fit)
    cstart = 4
    res[cnt, cstart:(cstart + 3)] = summary(fit)$tTable[2, c(1, 2, 4, 5)]
    fit = lme(as.formula(quad), data=data, random=~1|famid, na.action=na.omit)
    res[cnt, 3] = BIC(fit)
    cstart = 8
    res[cnt, cstart:(cstart + 3)] = summary(fit)$tTable[3, c(1, 2, 4, 5)]
    cstart = 12
    res[cnt, cstart:(cstart + 3)] = summary(fit)$tTable[2, c(1, 2, 4, 5)]
    cnt = cnt + 1
}
rownames(res) = names(data)[phen_vars]
# to export the results
write.csv(res,file=out_fname)
