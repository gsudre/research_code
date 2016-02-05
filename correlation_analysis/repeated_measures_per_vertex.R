fname_root = 'repeatedMeasuresANOVAperVetex_fromThalamusR_toOtherSubcortical_matchedDiffDSM5_2to1_perVSnv.RData'

# combine all the data ot get approximated MACAC
library(nlme)
seedData = thalamusR
brain_data = c('striatumL', 'striatumR', 'gpL', 'gpR')
nseeds = dim(seedData)[2]
txt = sprintf('%s[idx_base | idx_last,]', brain_data[1])
for (i in 2:length(brain_data)) {
    txt = sprintf('%s, %s[idx_base | idx_last,]', txt, brain_data[i])
}
eval(parse(text=sprintf('data=cbind(%s)', txt)))
nTotalVerts = dim(data)[2]
visit <- array(data='baseline',dim=length(idx))
visit[idx_last] = 'last'
visit = as.factor(visit)
res <- array(dim=c(nseeds, nTotalVerts))
for (s in 1:nseeds) {
    cat('\nseed', s, '/', nseeds)
    for (i in brain_data) {
        for (v in 1:nTotalVerts) {
            df = data.frame(vert=data[,v], seed=seedData[, s], group=group, visit=visit, subject=subject)
            fit = try(lme(seed ~ vert*group*visit, random=~1|subject/visit, data=df))
            if (length(fit)>1) {
                res[s, v] = anova(fit)$"F-value"[8]
            } else {
                res[s, v] = 0
            }
        }
    }
}
# save results to file
save(res, brain_data, file=fname)
