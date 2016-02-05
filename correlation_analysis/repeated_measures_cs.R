fnameRoot = '~/data/results/structural/repeatedMeasuresANOVA_last_toRcortex_matchedDiffDSM5_2to1_remVSper'

# combine all the data ot get approximated MACACC
library(nlme)
brain_data = c('cortexR')
cur_idx = idx_last

txt = sprintf('%s[cur_idx,]', brain_data[1])
if (length(brain_data) > 1) {
    for (i in 2:length(brain_data)) {
        txt = sprintf('%s, %s[cur_idx,]', txt, brain_data[i])
    }
}
eval(parse(text=sprintf('data=cbind(%s)', txt)))

# get approximate vector for all subjects and time points
approx = rowMeans(data)

# compute model for all brain regions
brain_data = c('thalamusR')
for (i in brain_data) {
    cat('Working on ', i, '\n')
    eval(parse(text=sprintf('data=%s[cur_idx,]', i)))
    nverts = dim(data)[2]
    res <- array(dim=c(nverts, 2))
    for (v in 1:nverts) {
        cat('\t', v, ' / ', nverts, '\n')
        df = data.frame(vert=data[,v], seed=approx, group=group[cur_idx], subject=subject[cur_idx])
        fit = try(lme(seed ~ vert*group, random=~1|subject, data=df))
        if (length(fit)>1) {
            res[v,1] = anova(fit)$"F-value"[4]
            res[v,2] = anova(fit)$"p-value"[4]
        } else {
            res[v,1] = 0
            res[v,2] = 1
        }
    }
    
    # save results to file
    fname = sprintf('%s_%s.txt', fnameRoot, i)
    write_vertices(res, fname, c('Slope.Fval', 'Slope.pval'))
}