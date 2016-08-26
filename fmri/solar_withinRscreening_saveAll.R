# runs linear mixed model for fMRI traits and saves beta, tstat and pval for all covariates
library(nlme)
library(MASS)

fname = '~/data/solar_paper_review/fmri_netMask_mean.csv'
out_fname = '~/data/solar_paper_review/all_covariates_fmri_maskMean_linear_interaction_squared.csv'
p_thresh = .05

data = read.csv(fname)
# all variables to use as phenotype
phen_vars = which(grepl("net", names(data)))

# which subjects to use
idx = 1:dim(data)[1]
sxs = c('inatt', 'HI', 'total')#, 'DX', 'DX_inatt', 'DX_hi', 'DX_comb')

# setting up output dataframe
df = data.frame(tracts=colnames(data[,phen_vars]))

terms = c('sx', 'sex', 'mean_enorm', 'I(mean_enorm^2)', 'age', 'sx:age', 'I(age^2)')
res = matrix(nrow=length(phen_vars), ncol=3*length(sxs)*length(terms))
cnames = vector()
for (s in sxs) {
    for (t in terms) {
        cnames = c(cnames, sprintf('%s_%s_beta', s, t))
        cnames = c(cnames, sprintf('%s_%s_tstat', s, t))
        cnames = c(cnames, sprintf('%s_%s_pval', s, t))
    }
}
colnames(res) = cnames

print(fname)
for (s in sxs) {
    cnt = 1
    for (v in phen_vars) {
        y = data[,v]
        eval(parse(text=sprintf('sx=data$%s', s)))
        fm = sprintf("y ~ %s", terms[1])
        for (t in 2:length(terms)) {
            fm = sprintf('%s + %s', fm, terms[t])
        }
        fm = as.formula(fm)
        fit = lme(fm, random=~1|famid, data=data, na.action=na.omit, method="ML")
        for (r in 2:dim(summary(fit)$tTable)[1]) {
            cname = rownames(summary(fit)$tTable)[r]
            cname = gsub("sexMale", "sex", cname)
            cname = gsub("ageBinLE22", "ageBin", cname)
            cstart = which(colnames(res) == sprintf("%s_%s_beta", s, cname))
            # beta
            res[cnt, cstart] = summary(fit)$tTable[r, 1]
            # tstat
            res[cnt, cstart + 1] = summary(fit)$tTable[r, 4]
            # pval
            res[cnt, cstart + 2] = summary(fit)$tTable[r, 5]
        }
        cnt = cnt + 1
    }
}
rownames(res) = names(data)[phen_vars]
# to export the results
write.csv(res,file=out_fname)
