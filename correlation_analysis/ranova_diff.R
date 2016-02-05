fname_root = 'ranova_diff_toOtherSubcortical_matchedDiffDSM5_2to1_perVSnv'
# combine all the data ot get approximated MACAC
library(nlme)
brain_data = c('gpR','striatumR','gpL','striatumL')
txt = sprintf('%s[idx_base | idx_last,]', brain_data[1])
for (i in 2:length(brain_data)) {
    txt = sprintf('%s, %s[idx_base | idx_last,]', txt, brain_data[i])
}
eval(parse(text=sprintf('data=cbind(%s)', txt)))
data = data[idx_last,]-data[idx_base,]

# get approximate vector for all subjects and time points
approx = rowMeans(data)

visit <- array(data='baseline',dim=length(idx))
visit[idx_last] = 'last'
visit = as.factor(visit)
# compute model for all brain regions
fit_names = vector(length=length(brain_data))
brain_data = c('thalamusR','thalamusL')
cnt = 1
for (i in brain_data) {
    cat('Working on ', i, '\n')
    eval(parse(text=sprintf('data=%s[idx_last,]-%s[idx_base,]', i, i)))
    nverts = dim(data)[2]
    res <- array(dim=c(nverts, 2))
    eval(parse(text=sprintf('fits_%s=list()', i)))
    eval(parse(text=sprintf('fit_names[[cnt]] = "fits_%s"', i)))
    cnt = cnt+1
    
    # do all the necessary tests (slope, variance)
    for (v in 1:nverts) {
        cat('\t', v, ' / ', nverts, '\n')
        df = data.frame(vert=data[,v], seed=approx, group=group[idx_last], 
                        subject=subject[idx_last])
        fit = try(lme(seed ~ vert*group, random=~1|subject, data=df))
        if (length(fit)>1) {
            res[v,1] = anova(fit)$"F-value"[4]
            res[v,2] = anova(fit)$"p-value"[4]
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