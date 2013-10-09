# combine all the data ot get approximated MACACC
library(lawstat)

txt_base = sprintf('%s[idx_base,]', brain_data[1])
txt_last = sprintf('%s[idx_last,]', brain_data[1])
for (i in 2:length(brain_data)) {
    txt_base = sprintf('%s, %s[idx_base,]', txt_base, brain_data[i])
    txt_last = sprintf('%s, %s[idx_last,]', txt_last, brain_data[i])
}
eval(parse(text=sprintf('baseData=cbind(%s)', txt_base)))
eval(parse(text=sprintf('lastData=cbind(%s)', txt_last)))
               
# calculate the slope for each subject
delta = lastData - baseData

# get approximate vector for all subjects
approx = rowMeans(delta)

# because we're looking at deltas, we need to get rid of half of the group variable
group = group[idx_last]

# compute model for all brain regions
for (i in brain_data) {
    print(sprintf('Working on %s', i))
    eval(parse(text=sprintf('baseData=%s[idx_base,]', i)))
    eval(parse(text=sprintf('lastData=%s[idx_last,]', i)))
    delta = lastData - baseData
    nverts = dim(delta)[2]
    res <- array(dim=c(nverts, 4))
    
    # do all the necessary tests (slope, variance)
    for (v in 1:nverts) {
        fit = lm(approx ~ group*delta[,v])
        lt <- levene.test(residuals(lm(approx ~ delta[,v])), group, location='median')
        res[v,1] = anova(fit)$"F value"[3]
        res[v,2] = anova(fit)$"Pr(>F)"[3]
        res[v,3] = lt$"F value"
        res[v,4] = lt$"Pr(>F)"
    }
    
    # save results to file
    fname = sprintf('~/data/results/structural/macacc_slopes_%s.txt', i)
    write_vertices(res, fname, c('Slope.Fval', 'Slope.pval', 'Levene.Fval', 'Levene.pval'))
}