# combine all the data ot get approximated MACACC
library(nlme)
# brain_data = c('dtL_cortex_SA_1473', 'dtR_cortex_SA_1473')
txt = sprintf('%s[idx_base | idx_last,]', brain_data[1])
for (i in 2:length(brain_data)) {
    txt = sprintf('%s, %s[idx_base | idx_last,]', txt, brain_data[i])
}
eval(parse(text=sprintf('data=cbind(%s)', txt)))

# get approximate vector for all subjects and time points
approx = rowMeans(data)

visit <- array(data='baseline',dim=length(idx))
visit[idx_last] = 'last'
visit = as.factor(visit)

# compute model for all brain regions
# brain_data = c('dtL_thalamus_1473', 'dtR_thalamus_1473', 
#                'dtL_striatum_1473', 'dtR_striatum_1473',
#                               'dtL_cortex_SA_1473', 'dtR_cortex_SA_1473',
#                'dtL_gp', 'dtR_gp')
for (i in brain_data) {
    cat('Working on ', i, '\n')
    eval(parse(text=sprintf('data=%s[idx_base | idx_last,]', i)))
    nverts = dim(data)[2]
    res <- array(dim=c(nverts, 2))
    
    # do all the necessary tests (slope, variance)
    for (v in 1:nverts) {
        cat('\t', v, ' / ', nverts, '\n')
        df = data.frame(vert=data[,v], seed=approx, group=group, age=age, visit=visit, subject=subject)
        fit = try(lme(seed ~ vert*group*visit, random=~1|subject, data=df))
        if (length(fit)>1) {
            res[v,1] = anova(fit)$"F-value"[8]
            res[v,2] = anova(fit)$"p-value"[8]
        } else {
            res[v,1] = 0
            res[v,2] = 1
        }
    }
    
    # save results to file
    fname = sprintf('~/data/results/structural/linearMACACC_noAge_subcortical_matched_2to1_%s.txt', i)
    write_vertices(res, fname, c('Slope.Fval', 'Slope.pval'))
}