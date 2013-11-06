fname_root = 'repeatedMeasuresANOVA_toLgpLstriatum_matchedDiffDSM5_2to1_perVSnv'

# combine all the data ot get approximated MACAC
library(nlme)
# determining the seed region
# brain_data = c(
# #                 'dtL_thalamus_1473', 'dtR_thalamus_1473', 
#                'dtL_striatum_1473', 'dtR_striatum_1473',
# #               'dtL_cortex_SA_1473', 'dtR_cortex_SA_1473'
#                'dtL_gp', 'dtR_gp'
#                 )
brain_data = c('gpL','striatumL')
# brain_data = c('thalamusR','thalamusR')
# verts = c(1092, 1093, 1096, 1099, 1230, 1232, 1235, 1236, 1238, 1370, 1372,
#           1376, 1502, 1505, 1507, 1509, 1510, 1626, 1630, 1633, 1634, 1638,
#           1639, 1761, 1763, 1765, 1766, 1770, 1771, 1890, 1894, 1895, 1897,
#           1898, 1900)
txt = sprintf('%s[idx_base | idx_last,]', brain_data[1])
for (i in 2:length(brain_data)) {
    txt = sprintf('%s, %s[idx_base | idx_last,]', txt, brain_data[i])
}
eval(parse(text=sprintf('data=cbind(%s)', txt)))
# get approximate vector for all subjects and time points
# approx = rowMeans(data[,verts])
approx = rowMeans(data)

visit <- array(data='baseline',dim=length(idx))
visit[idx_last] = 'last'
visit = as.factor(visit)
# compute model for all brain regions
# brain_data = c(
#                     'dtL_thalamus_1473', 'dtR_thalamus_1473'
#     #                'dtL_striatum_1473', 'dtR_striatum_1473',
# #     'dtL_cortex_SA_1473', 'dtR_cortex_SA_1473',
#     #                'dtL_gp', 'dtR_gp'
#              )
fit_names = vector(length=length(brain_data))
brain_data = c('thalamusL')
cnt = 1
for (i in brain_data) {
    cat('Working on ', i, '\n')
    eval(parse(text=sprintf('data=%s[idx_base | idx_last,]', i)))
    nverts = dim(data)[2]
    res <- array(dim=c(nverts, 2))
    eval(parse(text=sprintf('fits_%s=list()', i)))
    eval(parse(text=sprintf('fit_names[[cnt]] = "fits_%s"', i)))
    cnt = cnt+1
    
    # do all the necessary tests (slope, variance)
    for (v in 1:nverts) {
        cat('\t', v, ' / ', nverts, '\n')
        df = data.frame(vert=data[,v], seed=approx, group=group, visit=visit, subject=subject)
        fit = try(lme(seed ~ vert*group*visit, random=~1|subject/visit, data=df))
        if (length(fit)>1) {
            res[v,1] = anova(fit)$"F-value"[8]
            res[v,2] = anova(fit)$"p-value"[8]
            eval(parse(text=sprintf('fits_%s[[v]]=fit', i)))
        } else {
            res[v,1] = 0
            res[v,2] = 1
        }
    }
    
    # save results to file
    fname = sprintf('~/data/results/structural/%s_%s.txt', fname_root, i)
    write_vertices(res, fname, c('Slope.Fval', 'Slope.pval'))
}
save(list=fit_names, file=sprintf('~/data/results/structural/%s_fits.RData',fname_root))