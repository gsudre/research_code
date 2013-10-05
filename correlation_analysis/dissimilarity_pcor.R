# This one allows for connections between hemispheres
striatum = read.csv('~/data/structural/roisSum_striatumL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_dsm4.csv')
thalamus = read.csv('~/data/structural/roisSum_thalamusL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_dsm4.csv')
gp = read.csv('~/data/structural/roisSum_gpL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_dsm4.csv')
cortex = read.csv('~/data/structural/roisSum_cortexL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_dsm4.csv')

permuteCorrDiff <- function(data1B, data1L, data2B, data2L, nperms) 
{
    ds <- vector(mode = "numeric", length = nperms) 
    all_dataB = rbind(data1B, data2B)
    all_dataL = rbind(data1L, data2L)
    n1 = dim(data1B)[1]
    n2 = dim(data2B)[1]
    for (i in 1:nperms) {
        perm_labels <- sample.int(n1+n2, replace = FALSE)
        perm_dataB <- all_dataB[perm_labels, ]
        perm_dataL <- all_dataL[perm_labels, ]
        pmat1b = perm_dataB[1:n1, ]
        pmat2b = perm_dataB[(n1+1):(n1+n2), ]
        pmat1l = perm_dataL[1:n1, ]
        pmat2l = perm_dataL[(n1+1):(n1+n2), ]
        cor1b = cor(pmat1b)
        cor2b = cor(pmat2b)
        cor1l = cor(pmat1l)
        cor2l = cor(pmat2l)
        deltaCor1 = cor1l - cor1b
        deltaCor2 = cor2l - cor2b
        ds[i] = 1-cor(deltaCor1[upper.tri(deltaCor1)], deltaCor2[upper.tri(deltaCor2)], method="spearman")
    }
    return(ds)
}

bootstrapCorrDiff <- function(fixed_dataB, fixed_dataL, dataB, dataL, nperms) 
{
    ds <- vector(mode = "numeric", length = nperms) 
    cor1b = cor(fixed_dataB)
    cor1l = cor(fixed_dataL)
    deltaCor1 = cor1l - cor1b
    for (i in 1:nperms) {
        perm_labels <- sample.int(dim(dataB)[1], replace = TRUE)
        perm_dataB <- dataB[perm_labels, ]
        perm_dataL <- dataL[perm_labels, ]
        cor2b = cor(perm_dataB)
        cor2l = cor(perm_dataL)
        deltaCor2 = cor2l - cor2b
        ds[i] = 1-cor(deltaCor1[upper.tri(deltaCor1)], deltaCor2[upper.tri(deltaCor2)], method="spearman")
    }
    return(ds)
}

permuteCorr <- function(data1, data2, nperms) 
{
    ds <- vector(mode = "numeric", length = nperms) 
    all_data = rbind(data1, data2)
    n1 = dim(data1)[1]
    n2 = dim(data2)[1]
    for (i in 1:nperms) {
        perm_labels <- sample.int(dim(all_data)[1], replace = FALSE)
        perm_data <- all_data[perm_labels, ]
        pmat1 = perm_data[1:n1, ]
        pmat2 = perm_data[(n1+1):(n1+n2), ]
        cor1 = pcor(pmat1)$estimate
        cor2 = pcor(pmat2)$estimate
        ds[i] = 1-cor(cor1[upper.tri(cor1)], cor2[upper.tri(cor2)], method="spearman")
    }
    return(ds)
}

bootstrapCorr <- function(fixed_data, data, nperms) 
{
    ds <- vector(mode = "numeric", length = nperms) 
    cor1 = pcor(fixed_data)$estimate
    for (i in 1:nperms) {
        perm_labels <- sample.int(dim(data)[1], replace = TRUE)
        perm_data <- data[perm_labels, ]
        cor2 = pcor(perm_data)$estimate
        ds[i] = 1-cor(cor1[upper.tri(cor1)], cor2[upper.tri(cor2)], method="spearman")
    }
    return(ds)
}

error.bar <- function(x, y, upper, lower=upper, length=0.1,...){
    if(length(x) != length(y) | length(y) !=length(lower) | length(lower) != length(upper))
        stop("vectors must be same length")
    arrows(x,y+upper, x, y-lower, angle=90, code=3, length=length, ...)
}

idxp = striatum$group=="persistent" & striatum$visit=="baseline"
idxr = striatum$group=="remission" & striatum$visit=="baseline"
idxn = striatum$group=="NV" & striatum$visit=="baseline"

pmatb = cbind(striatum[idxp,4:dim(striatum)[2]], thalamus[idxp,4:dim(thalamus)[2]],
             cortex[idxp,4:dim(cortex)[2]], gp[idxp,4:dim(gp)[2]])
rmatb = cbind(striatum[idxr,4:dim(striatum)[2]], thalamus[idxr,4:dim(thalamus)[2]],
             cortex[idxr,4:dim(cortex)[2]], gp[idxr,4:dim(gp)[2]])
nmatb = cbind(striatum[idxn,4:dim(striatum)[2]], thalamus[idxn,4:dim(thalamus)[2]],
             cortex[idxn,4:dim(cortex)[2]], gp[idxn,4:dim(gp)[2]])

pcorb = pcor(pmatb)$estimate
rcorb = pcor(rmatb)$estimate
ncorb = pcor(nmatb)$estimate

dnpb = 1-cor(ncorb[upper.tri(ncorb)], pcorb[upper.tri(pcorb)], method="spearman")
dnrb = 1-cor(ncorb[upper.tri(ncorb)], rcorb[upper.tri(rcorb)], method="spearman")
dprb = 1-cor(pcorb[upper.tri(pcorb)], rcorb[upper.tri(rcorb)], method="spearman")

p_perms = 1000
dists = c(dnrb, dnpb, dprb)
pval = sum(permuteCorr(nmatb, rmatb, p_perms)>dnrb)/p_perms
pval = min(pval,1-pval)
names(dists)[1] = sprintf('NVvsRem\np<%.3f', pval)
pval = sum(permuteCorr(nmatb, pmatb, p_perms)>dnpb)/p_perms
pval = min(pval,1-pval)
names(dists)[2] = sprintf('NVvsPer\np<%.3f', pval)
pval = sum(permuteCorr(pmatb, rmatb, p_perms)>dprb)/p_perms
pval = min(pval,1-pval)
names(dists)[3] = sprintf('PervsRem\np<%.3f', pval)
par(mfrow=c(1,3))
s_dists = sort(dists, index.return=TRUE)
bp = barplot(s_dists$x, main='Baseline', ylim=c(0, 1.2))

#####################

idxp = striatum$group=="persistent" & striatum$visit=="last"
idxr = striatum$group=="remission" & striatum$visit=="last"
idxn = striatum$group=="NV" & striatum$visit=="last"

pmatl = cbind(striatum[idxp,4:dim(striatum)[2]], thalamus[idxp,4:dim(thalamus)[2]],
             cortex[idxp,4:dim(cortex)[2]], gp[idxp,4:dim(gp)[2]])
rmatl = cbind(striatum[idxr,4:dim(striatum)[2]], thalamus[idxr,4:dim(thalamus)[2]],
             cortex[idxr,4:dim(cortex)[2]], gp[idxr,4:dim(gp)[2]])
nmatl = cbind(striatum[idxn,4:dim(striatum)[2]], thalamus[idxn,4:dim(thalamus)[2]],
             cortex[idxn,4:dim(cortex)[2]], gp[idxn,4:dim(gp)[2]])

pcorl = pcor(pmatl)$estimate
rcorl = pcor(rmatl)$estimate
ncorl = pcor(nmatl)$estimate

dnpl = 1-cor(ncorl[upper.tri(ncorl)], pcorl[upper.tri(pcorl)], method="spearman")
dnrl = 1-cor(ncorl[upper.tri(ncorl)], rcorl[upper.tri(rcorl)], method="spearman")
dprl = 1-cor(pcorl[upper.tri(pcorl)], rcorl[upper.tri(rcorl)], method="spearman")

dists = c(dnrl, dnpl, dprl)
pval = sum(permuteCorr(nmatl, rmatl, p_perms)>dnrl)/p_perms
pval = min(pval,1-pval)
names(dists)[1] = sprintf('NVvsRem\np<%.3f', pval)
pval = sum(permuteCorr(nmatl, pmatl, p_perms)>dnpl)/p_perms
pval = min(pval,1-pval)
names(dists)[2] = sprintf('NVvsPer\np<%.3f', pval)
pval = sum(permuteCorr(pmatl, rmatl, p_perms)>dprl)/p_perms
pval = min(pval,1-pval)
names(dists)[3] = sprintf('PervsRem\np<%.3f', pval)
s_dists = sort(dists, index.return=TRUE)
bp = barplot(s_dists$x, main='Follow up', ylim=c(0, 1.2))

# now we look at FU-baseline differences
pcorDelta = pcorl - pcorb
rcorDelta = rcorl - rcorb
ncorDelta = ncorl - ncorb
dDeltaNR = 1-cor(ncorDelta[upper.tri(ncorDelta)], rcorDelta[upper.tri(rcorDelta)], method="spearman")
dDeltaNP = 1-cor(ncorDelta[upper.tri(ncorDelta)], pcorDelta[upper.tri(pcorDelta)], method="spearman")
dDeltaPR = 1-cor(pcorDelta[upper.tri(pcorDelta)], rcorDelta[upper.tri(rcorDelta)], method="spearman")
dists = c(dDeltaNR, dDeltaNP, dDeltaPR)
pval = sum(permuteCorrDiff(nmatb, nmatl, rmatb, rmatl, p_perms)>dDeltaNR)/p_perms
pval = min(pval,1-pval)
names(dists)[1] = sprintf('NVvsRem\np<%.3f', pval)
pval = sum(permuteCorrDiff(nmatb, nmatl, pmatb, pmatl, p_perms)>dDeltaNP)/p_perms
pval = min(pval,1-pval)
names(dists)[2] = sprintf('NVvsPer\np<%.3f', pval)
pval = sum(permuteCorrDiff(pmatb, pmatl, rmatb, rmatl, p_perms)>dDeltaPR)/p_perms
pval = min(pval,1-pval)
names(dists)[3] = sprintf('PervsRem\np<%.3f', pval)
s_dists = sort(dists, index.return=TRUE)
bp = barplot(s_dists$x, main='Deltas FU-Baseline', ylim=c(0, 1.2))
