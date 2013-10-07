# Hemisphere-dependent partial correlation analysis
hemi = 'R'
dsm = 4
p_perms = 10
striatum = read.csv(sprintf('~/data/structural/roisSum_striatum%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_dsm%d.csv', hemi, dsm))
thalamus = read.csv(sprintf('~/data/structural/roisSum_thalamus%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_dsm%d.csv', hemi, dsm))
gp = read.csv(sprintf('~/data/structural/roisSum_gp%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_dsm%d.csv', hemi, dsm))
cortex = read.csv(sprintf('~/data/structural/roisSum_cortex%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_dsm%d.csv', hemi, dsm))

permuteCorrDiff <- function(data1B, data1L, data2B, data2L, nperms) 
{
    ds <- vector(mode = "numeric", length = nperms) 
    alL_dataB = rbind(data1B, data2B)
    alL_dataL = rbind(data1L, data2L)
    n1 = dim(data1B)[1]
    n2 = dim(data2B)[1]
    for (i in 1:nperms) {
        perm_labels <- sample.int(n1+n2, replace = FALSE)
        perm_dataB <- alL_dataB[perm_labels, ]
        perm_dataL <- alL_dataL[perm_labels, ]
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

permuteCorr <- function(data1, data2, nperms) 
{
    ds <- vector(mode = "numeric", length = nperms) 
    alL_data = rbind(data1, data2)
    n1 = dim(data1)[1]
    n2 = dim(data2)[1]
    for (i in 1:nperms) {
        perm_labels <- sample.int(dim(alL_data)[1], replace = FALSE)
        perm_data <- alL_data[perm_labels, ]
        pmat1 = perm_data[1:n1, ]
        pmat2 = perm_data[(n1+1):(n1+n2), ]
        cor1 = pcor(pmat1)$estimate
        cor2 = pcor(pmat2)$estimate
        ds[i] = 1-cor(cor1[upper.tri(cor1)], cor2[upper.tri(cor2)], method="spearman")
    }
    return(ds)
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
bp = barplot(s_dists$x, main=sprintf('Baseline (%s)', hemi), ylim=c(0, 1.2))

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
bp = barplot(s_dists$x, main=sprintf('Follow up (%s)', hemi), ylim=c(0, 1.2))

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
bp = barplot(s_dists$x, main=sprintf('Deltas FU-Baseline (%s)', hemi), ylim=c(0, 1.2))
