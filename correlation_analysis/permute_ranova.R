nperms = 10
source('~/research_code/correlation_analysis/macacc_massage_data_matched.R')

set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )

fname_root = 'perm_repeatedMeasuresANOVA_subcortical_matchedDiffDSM4_perVSnv'
max_Fval = vector(mode="numeric", length=nperms)

# combine all the data ot get approximated MACAC
library(nlme)
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
brain_data = c('dtL_thalamus_1473', 'dtR_thalamus_1473', 
               'dtL_striatum_1473', 'dtR_striatum_1473',
               #                               'dtL_cortex_SA_1473', 'dtR_cortex_SA_1473',
               'dtL_gp', 'dtR_gp')
fit_names = vector(length=length(brain_data))

for (p in 1:nperms) {
    cat('Working on perm', p, '/', nperms, '\n')
    perm_labels <- sample.int(length(group), replace = FALSE)
    perm_group = group[perm_labels]
    perm_visit = visit[perm_labels]
    perm_subject = subject[perm_labels]
    cnt = 1
    for (i in brain_data) {
        eval(parse(text=sprintf('data=%s[idx_base | idx_last,]', i)))
        nverts = dim(data)[2]
        res <- array(dim=c(nverts, 2))
        cnt = cnt+1
        
        # do all the necessary tests (slope, variance)
        for (v in 1:nverts) {
            df = data.frame(vert=data[,v], seed=approx, group=perm_group, visit=perm_visit, subject=perm_subject)
            fit = try(lme(seed ~ vert*group*visit, random=~1|subject/visit, data=df))
            if (length(fit)>1) {
                res[v,1] = anova(fit)$"F-value"[8]
                res[v,2] = anova(fit)$"p-value"[8]
            } else {
                res[v,1] = 0
                res[v,2] = 1
            }
        }
        max_Fval[p] = max(max_Fval[p], max(res[,1]))
    }
}
save(max_Fval, file=sprintf('~/data/results/structural/%s_%4g.RData',fname_root, floor(runif(1, 1, 9999))))