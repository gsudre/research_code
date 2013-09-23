striatum = read.csv('~/data/structural/rois_striatumL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')
thalamus= read.csv('~/data/structural/rois_thalamusL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')
gp = read.csv('~/data/structural/rois_gpL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')
cortex = read.csv('~/data/structural/rois_cortexL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')

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
        cor1 = cor(pmat1)
        cor2 = cor(pmat2)
        ds[i] = 1-cor(cor1[upper.tri(cor1)], cor2[upper.tri(cor2)], method="spearman")
    }
    return(ds)
}

bootstrapCorr <- function(fixed_data, data, nperms) 
{
    ds <- vector(mode = "numeric", length = nperms) 
    cor1 = cor(fixed_data)
    for (i in 1:nperms) {
        perm_labels <- sample.int(dim(data)[1], replace = TRUE)
        perm_data <- data[perm_labels, ]
        cor2 = cor(perm_data)
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
# idxa = striatum$group=="ADHD" & striatum$visit=="baseline"
idxa = idxr | idxp

pmatb = cbind(striatum[idxp,4:dim(striatum)[2]], thalamus[idxp,4:dim(thalamus)[2]],
             cortex[idxp,4:dim(cortex)[2]], gp[idxp,4:dim(gp)[2]])
rmatb = cbind(striatum[idxr,4:dim(striatum)[2]], thalamus[idxr,4:dim(thalamus)[2]],
             cortex[idxr,4:dim(cortex)[2]], gp[idxr,4:dim(gp)[2]])
nmatb = cbind(striatum[idxn,4:dim(striatum)[2]], thalamus[idxn,4:dim(thalamus)[2]],
             cortex[idxn,4:dim(cortex)[2]], gp[idxn,4:dim(gp)[2]])
amatb = cbind(striatum[idxa,4:dim(striatum)[2]], thalamus[idxa,4:dim(thalamus)[2]],
             cortex[idxa,4:dim(cortex)[2]], gp[idxa,4:dim(gp)[2]])

# pmat = cbind(striatum[idxp,4:dim(striatum)[2]], thalamus[idxp,4:dim(thalamus)[2]],
#              gp[idxp,4:dim(gp)[2]])
# rmat = cbind(striatum[idxr,4:dim(striatum)[2]], thalamus[idxr,4:dim(thalamus)[2]],
#              gp[idxr,4:dim(gp)[2]])
# nmat = cbind(striatum[idxn,4:dim(striatum)[2]], thalamus[idxn,4:dim(thalamus)[2]],
#              gp[idxn,4:dim(gp)[2]])
# amat = cbind(striatum[idxa,4:dim(striatum)[2]], thalamus[idxa,4:dim(thalamus)[2]],
#              gp[idxa,4:dim(gp)[2]])

# pmat = cbind(striatum[idxp,4:dim(striatum)[2]], thalamus[idxp,4:dim(thalamus)[2]])
# rmat = cbind(striatum[idxr,4:dim(striatum)[2]], thalamus[idxr,4:dim(thalamus)[2]])
# nmat = cbind(striatum[idxn,4:dim(striatum)[2]], thalamus[idxn,4:dim(thalamus)[2]])
# amat = cbind(striatum[idxa,4:dim(striatum)[2]], thalamus[idxa,4:dim(thalamus)[2]])

pcorb = cor(pmatb)
rcorb = cor(rmatb)
ncorb = cor(nmatb)
acorb = cor(amatb)

dnab = 1-cor(ncorb[upper.tri(ncorb)], acorb[upper.tri(acorb)], method="spearman")
dnpb = 1-cor(ncorb[upper.tri(ncorb)], pcorb[upper.tri(pcorb)], method="spearman")
dnrb = 1-cor(ncorb[upper.tri(ncorb)], rcorb[upper.tri(rcorb)], method="spearman")
dprb = 1-cor(pcorb[upper.tri(pcorb)], rcorb[upper.tri(rcorb)], method="spearman")

b_perms = 1000
p_perms = 1000
err_dnab = sd(bootstrapCorr(nmatb, amatb, b_perms))
err_dnrb = sd(bootstrapCorr(nmatb, rmatb, b_perms))
err_dnpb = sd(bootstrapCorr(nmatb, pmatb, b_perms))
err_dprb = sd(bootstrapCorr(pmatb, rmatb, b_perms))
dists = c(dnab, dnrb, dnpb, dprb)
err_dists = c(err_dnab, err_dnrb, err_dnpb, err_dprb)
names(dists)[1] = sprintf('NVvsADHD\np<%.3f', sum(permuteCorr(nmatb, amatb, b_perms)>dnab)/p_perms)
names(dists)[2] = sprintf('NVvsRem\np<%.3f', sum(permuteCorr(nmatb, rmatb, b_perms)>dnrb)/p_perms)
names(dists)[3] = sprintf('NVvsPer\np<%.3f', sum(permuteCorr(nmatb, pmatb, b_perms)>dnpb)/p_perms)
names(dists)[4] = sprintf('PervsRem\np<%.3f', sum(permuteCorr(pmatb, rmatb, b_perms)>dprb)/p_perms)
s_dists = sort(dists, index.return=TRUE)
par(mfrow=c(1,3))
bp = barplot(s_dists$x, main='Baseline', ylim=c(0, 0.7))
error.bar(bp, s_dists$x, err_dists[s_dists$ix])

#####################

idxp = striatum$group=="persistent" & striatum$visit=="last"
idxr = striatum$group=="remission" & striatum$visit=="last"
idxn = striatum$group=="NV" & striatum$visit=="last"
# idxa = striatum$group=="ADHD" & striatum$visit=="last"
idxa = idxr | idxp

pmatl = cbind(striatum[idxp,4:dim(striatum)[2]], thalamus[idxp,4:dim(thalamus)[2]],
             cortex[idxp,4:dim(cortex)[2]], gp[idxp,4:dim(gp)[2]])
rmatl = cbind(striatum[idxr,4:dim(striatum)[2]], thalamus[idxr,4:dim(thalamus)[2]],
             cortex[idxr,4:dim(cortex)[2]], gp[idxr,4:dim(gp)[2]])
nmatl = cbind(striatum[idxn,4:dim(striatum)[2]], thalamus[idxn,4:dim(thalamus)[2]],
             cortex[idxn,4:dim(cortex)[2]], gp[idxn,4:dim(gp)[2]])
amatl = cbind(striatum[idxa,4:dim(striatum)[2]], thalamus[idxa,4:dim(thalamus)[2]],
             cortex[idxa,4:dim(cortex)[2]], gp[idxa,4:dim(gp)[2]])

pcorl = cor(pmatl)
rcorl = cor(rmatl)
ncorl = cor(nmatl)
acorl = cor(amatl)

dnal = 1-cor(ncorl[upper.tri(ncorl)], acorl[upper.tri(acorl)], method="spearman")
dnpl = 1-cor(ncorl[upper.tri(ncorl)], pcorl[upper.tri(pcorl)], method="spearman")
dnrl = 1-cor(ncorl[upper.tri(ncorl)], rcorl[upper.tri(rcorl)], method="spearman")
dprl = 1-cor(pcorl[upper.tri(pcorl)], rcorl[upper.tri(rcorl)], method="spearman")

err_dnal = sd(bootstrapCorr(nmatl, amatl, b_perms))
err_dnrl = sd(bootstrapCorr(nmatl, rmatl, b_perms))
err_dnpl = sd(bootstrapCorr(nmatl, pmatl, b_perms))
err_dprl = sd(bootstrapCorr(pmatl, rmatl, b_perms))
dists = c(dnal, dnrl, dnpl, dprl)
err_dists = c(err_dnal, err_dnrl, err_dnpl, err_dprl)
names(dists)[1] = sprintf('NVvsADHD\np<%.3f', sum(permuteCorr(nmatl, amatl, b_perms)>dnal)/p_perms)
names(dists)[2] = sprintf('NVvsRem\np<%.3f', sum(permuteCorr(nmatl, rmatl, b_perms)>dnrl)/p_perms)
names(dists)[3] = sprintf('NVvsPer\np<%.3f', sum(permuteCorr(nmatl, pmatl, b_perms)>dnpl)/p_perms)
names(dists)[4] = sprintf('PervsRem\np<%.3f', sum(permuteCorr(pmatl, rmatl, b_perms)>dprl)/p_perms)
s_dists = sort(dists, index.return=TRUE)
bp = barplot(s_dists$x, main='Follow up', ylim=c(0, 0.7))
error.bar(bp, s_dists$x, err_dists[s_dists$ix])

# now we look at FU-baseline differences
pdelta = pmatl - pmatb
rdelta = rmatl - rmatb
ndelta = nmatl - nmatb
adelta = amatl - amatb
pcorDelta = cor(pdelta)
rcorDelta = cor(rdelta)
ncorDelta = cor(ndelta)
acorDelta = cor(adelta)
dDeltaNA = 1-cor(ncorDelta[upper.tri(ncorDelta)], acorDelta[upper.tri(acorDelta)], method="spearman")
dDeltaNR = 1-cor(ncorDelta[upper.tri(ncorDelta)], rcorDelta[upper.tri(rcorDelta)], method="spearman")
dDeltaNP = 1-cor(ncorDelta[upper.tri(ncorDelta)], pcorDelta[upper.tri(pcorDelta)], method="spearman")
dDeltaPR = 1-cor(ncorDelta[upper.tri(ncorDelta)], pcorDelta[upper.tri(pcorDelta)], method="spearman")
err_dDeltaNA = sd(bootstrapCorr(ndelta, adelta, b_perms))
err_dDeltaNR = sd(bootstrapCorr(ndelta, rdelta, b_perms))
err_dDeltaNP = sd(bootstrapCorr(ndelta, pdelta, b_perms))
err_dDeltaPR = sd(bootstrapCorr(pdelta, rdelta, b_perms))
dists = c(dDeltaNA, dDeltaNR, dDeltaNP, dDeltaPR)
err_dists = c(err_dDeltaNA, err_dDeltaNR, err_dDeltaNP, err_dDeltaPR)
names(dists)[1] = sprintf('NVvsADHD\np<%.3f', sum(permuteCorr(ndelta, adelta, b_perms)>dDeltaNA)/p_perms)
names(dists)[2] = sprintf('NVvsRem\np<%.3f', sum(permuteCorr(ndelta, rdelta, b_perms)>dDeltaNR)/p_perms)
names(dists)[3] = sprintf('NVvsPer\np<%.3f', sum(permuteCorr(ndelta, pdelta, b_perms)>dDeltaNP)/p_perms)
names(dists)[4] = sprintf('PervsRem\np<%.3f', sum(permuteCorr(pdelta, rdelta, b_perms)>dDeltaPR)/p_perms)
s_dists = sort(dists, index.return=TRUE)
bp = barplot(s_dists$x, main='Deltas FU-Baseline', ylim=c(0, 1.2))
error.bar(bp, s_dists$x, err_dists[s_dists$ix])