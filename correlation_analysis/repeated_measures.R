fname_root = 'repeatedMeasuresANOVA_seed%s_matchedDiffDSM5_2to1'

gLabels = sort(unique(c(g1,g2,g3)))
if (gLabels[1]=='NV') {
    if (gLabels[2]=='persistent') {
        fname_root = paste(fname_root,'_perVSnv',sep='')
    } else if (gLabels[2]=='remission') {
        fname_root = paste(fname_root,'_remVSnv',sep='')
    }
} else {
    fname_root = paste(fname_root,'_perVSrem',sep='')
}

# combine all the data ot get approximated MACAC
library(nlme)
# determining the seed region
brain_data = c('thalamusR')
fname_root = sprintf(fname_root,brain_data[1])
txt = sprintf('%s[idx_base | idx_last,]', brain_data[1])
# if (length(brain_data) > 1) {
#     for (i in 2:length(brain_data)) {
#         txt = sprintf('%s, %s[idx_base | idx_last,]', txt, brain_data[i])
#     }
# }
eval(parse(text=sprintf('data=cbind(%s)', txt)))
# get approximate vector for all subjects and time points
roi = 1:dim(data)[2]
approx = rowMeans(data[,roi])

visit <- array(data='baseline',dim=length(idx))
visit[idx_last] = 'last'
visit = as.factor(visit)
# compute model for all brain regions
brain_data = c('striatumR')
fit_names = vector(length=length(brain_data))
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
    fname = sprintf('~/data/results/structural_v2/%s_%s.txt', fname_root, i)
    write_vertices(res, fname, c('Slope.Fval', 'Slope.pval'))
}
save(list=fit_names, file=sprintf('~/data/results/structural_v2/%s_fits.RData',fname_root))