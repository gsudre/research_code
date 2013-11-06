nperms = 2
source('~/research_code/correlation_analysis/macacc_massage_data_matched_2to1.R')

set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )

fname_root = 'perm_repeatedMeasuresANOVA_toOtherSubcortical_matchedDiffDSM5_2to1_perVSnv'
max_Fval = vector(mode="numeric", length=nperms)

library(nlme)
# combine all the data ot get approximated MACAC
brain_data = c('striatumL', 'striatumR', 'gpL', 'gpR')
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
brain_data = c('thalamusL', 'thalamusR')

for (p in 1:nperms) {
    cat('Working on perm', p, '/', nperms, '\n')
    # we want to only flip group and visit labels, but keep subjects constant
    # such that if a subject is in one group at baseline, it's in the same group
    # in FU. the data is organized all g1, then all g2. in subject, we have 
    # baseline and fu for subj1, then for subj2, etc...
    # for every subject, choose whether we'll flip the visit labels or not
    perm_visit = visit
    cnt = 1
    while (cnt < length(perm_visit)-1) {
        if (runif(1) > .5) { 
            old = perm_visit[cnt+1]
            perm_visit[cnt+1] = perm_visit[cnt]
            perm_visit[cnt] = old
        }
        cnt = cnt + 2
    }
    # decide random group label of each subject (not observation!), being careful
    # to preserve group ratios
    subj_labels = group[seq(1,length(group),2)]
    perm_labels <- sample.int(length(subj_labels), replace = FALSE)
    perm_subj_labels = subj_labels[perm_labels]
    perm_group = group
    cnt = 1
    for (label in perm_subj_labels) {
        perm_group[cnt] = label
        perm_group[cnt+1] = label
        cnt = cnt + 2
    }
    
    for (i in brain_data) {
        eval(parse(text=sprintf('data=%s[idx_base | idx_last,]', i)))
        nverts = dim(data)[2]
        res <- array(dim=c(nverts, 2))
        for (v in 1:nverts) {
            df = data.frame(vert=data[,v], seed=approx, group=perm_group, visit=perm_visit, subject=subject)
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
save(max_Fval, file=sprintf('~/data/results/structural/perms/ranova/%s_%4g.RData',fname_root, floor(runif(1, 1, 9999))))