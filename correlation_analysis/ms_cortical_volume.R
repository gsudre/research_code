source('~/research_code/correlation_analysis/massage_volume_data.R')

# start by using left thalamus as seed
approx = subcortexVol[,3]
res = array(dim=c(26, 2))
cnt = 1
for (v in seq(2,52,2)) {
    df = data.frame(vert=cortexVol[,v], seed=approx, group=group, visit=visit, subject=subject)
    fit = try(lme(seed ~ vert*group*visit, random=~1|subject/visit, data=df))
    if (length(fit)>1) {
        res[cnt,1] = anova(fit)$"F-value"[8]
        res[cnt,2] = anova(fit)$"p-value"[8]
    } else {
        res[cnt,1] = 0
        res[cnt,2] = 1
    }
    cnt = cnt + 1
}
thalamusCortexL = res

# now the right thalamus
approx = subcortexVol[,6]
res = array(dim=c(26, 2))
cnt = 1
for (v in seq(1,52,2)) {
    df = data.frame(vert=cortexVol[,v], seed=approx, group=group, visit=visit, subject=subject)
    fit = try(lme(seed ~ vert*group*visit, random=~1|subject/visit, data=df))
    if (length(fit)>1) {
        res[cnt,1] = anova(fit)$"F-value"[8]
        res[cnt,2] = anova(fit)$"p-value"[8]
    } else {
        res[cnt,1] = 0
        res[cnt,2] = 1
    }
    cnt = cnt + 1
}
thalamusCortexR = res

# from cortex to the left thalamus
approx = rowMeans(cortexVol[,seq(2,52,2)])
res = array(dim=c(11, 2))
cnt = 1
for (v in 7:17) {
    df = data.frame(vert=subcortexVol[,v], seed=approx, group=group, visit=visit, subject=subject)
    fit = try(lme(seed ~ vert*group*visit, random=~1|subject/visit, data=df))
    if (length(fit)>1) {
        res[cnt,1] = anova(fit)$"F-value"[8]
        res[cnt,2] = anova(fit)$"p-value"[8]
    } else {
        res[cnt,1] = 0
        res[cnt,2] = 1
    }
    cnt = cnt + 1
}
cortexThalamusL = res

# and then to the right thalamus
approx = rowMeans(cortexVol[,seq(1,52,2)])
res = array(dim=c(11, 2))
cnt = 1
for (v in 18:28) {
    df = data.frame(vert=subcortexVol[,v], seed=approx, group=group, visit=visit, subject=subject)
    fit = try(lme(seed ~ vert*group*visit, random=~1|subject/visit, data=df))
    if (length(fit)>1) {
        res[cnt,1] = anova(fit)$"F-value"[8]
        res[cnt,2] = anova(fit)$"p-value"[8]
    } else {
        res[cnt,1] = 0
        res[cnt,2] = 1
    }
    cnt = cnt + 1
}
cortexThalamusR = res

# now we try to summarize the results
thresh = .01
brain_data = c('thalamusCortexL','thalamusCortexR',
               'cortexThalamusL','cortexThalamusR')
for (b in brain_data) {
    eval(parse(text=sprintf('pvals=%s[,2]', b)))
    eval(parse(text=sprintf('fvals=%s[,1]', b)))
    adj_pvals = p.adjust(pvals, method='fdr')
    cat('\nConnections:', b)
    cat('\nThreshold: p <', thresh)
    cat('\nMaximum F-val:', max(abs(fvals)))
    cat('\nGood uncorrected pvals:', sum(pvals<thresh), '/', length(pvals))
    cat('\nMinimum uncorrected F-val:', min(abs(fvals[pvals<thresh])))
    cat('\nGood FDR pvals:', sum(adj_pvals<thresh), '/', length(adj_pvals))
    cat('\nMinimum FDR F-val:', min(abs(fvals[adj_pvals<thresh])))
}


#### ========= ####

# now we try the big matrix approach. First, left hemisphere
data = rbind(cortexVol[,seq(2,52,2)], subcortexVol[,7:17])