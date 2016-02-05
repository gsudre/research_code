striatum = read.csv('~/data/structural/roisSum_striatumL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')
thalamus= read.csv('~/data/structural/roisSum_thalamusL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')
gp = read.csv('~/data/structural/roisSum_gpL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')
cortex = read.csv('~/data/structural/roisSum_cortexL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')

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
        cov1 = cov(pmat1)
        cov2 = cov(pmat2)
        ds[i] = 1-cor(cov1[upper.tri(cov1)], cov2[upper.tri(cov2)], method="spearman")
    }
    return(ds)
}

bootstrapCorr <- function(fixed_data, data, nperms) 
{
    ds <- vector(mode = "numeric", length = nperms) 
    cov1 = cov(fixed_data)
    for (i in 1:nperms) {
        perm_labels <- sample.int(dim(data)[1], replace = TRUE)
        perm_data <- data[perm_labels, ]
        cov2 = cov(perm_data)
        ds[i] = 1-cor(cov1[upper.tri(cov1)], cov2[upper.tri(cov2)], method="spearman")
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

# pmatb = cbind(striatum[idxp,4:dim(striatum)[2]], thalamus[idxp,4:dim(thalamus)[2]],
#               gp[idxp,4:dim(gp)[2]])
# rmatb = cbind(striatum[idxr,4:dim(striatum)[2]], thalamus[idxr,4:dim(thalamus)[2]],
#               gp[idxr,4:dim(gp)[2]])
# nmatb = cbind(striatum[idxn,4:dim(striatum)[2]], thalamus[idxn,4:dim(thalamus)[2]],
#               gp[idxn,4:dim(gp)[2]])
# amatb = cbind(striatum[idxa,4:dim(striatum)[2]], thalamus[idxa,4:dim(thalamus)[2]],
#               gp[idxa,4:dim(gp)[2]])

# pmatb = cbind(striatum[idxp,4:dim(striatum)[2]], thalamus[idxp,4:dim(thalamus)[2]])
# rmatb = cbind(striatum[idxr,4:dim(striatum)[2]], thalamus[idxr,4:dim(thalamus)[2]])
# nmatb = cbind(striatum[idxn,4:dim(striatum)[2]], thalamus[idxn,4:dim(thalamus)[2]])
# amatb = cbind(striatum[idxa,4:dim(striatum)[2]], thalamus[idxa,4:dim(thalamus)[2]])

pcovb = cov(pmatb)
rcovb = cov(rmatb)
ncovb = cov(nmatb)
acovb = cov(amatb)

dnab = 1-cor(ncovb[upper.tri(ncovb)], acovb[upper.tri(acovb)], method="spearman")
dnpb = 1-cor(ncovb[upper.tri(ncovb)], pcovb[upper.tri(pcovb)], method="spearman")
dnrb = 1-cor(ncovb[upper.tri(ncovb)], rcovb[upper.tri(rcovb)], method="spearman")
dprb = 1-cor(pcovb[upper.tri(pcovb)], rcovb[upper.tri(rcovb)], method="spearman")

b_perms = 1000
p_perms = 1000
err_dnab = sd(bootstrapCorr(nmatb, amatb, b_perms))
err_dnrb = sd(bootstrapCorr(nmatb, rmatb, b_perms))
err_dnpb = sd(bootstrapCorr(nmatb, pmatb, b_perms))
err_dprb = sd(bootstrapCorr(pmatb, rmatb, b_perms))
dists = c(dnab, dnrb, dnpb, dprb)
err_dists = c(err_dnab, err_dnrb, err_dnpb, err_dprb)
names(dists)[1] = sprintf('NVvsADHD\np<%.3f', sum(permuteCorr(nmatb, amatb, p_perms)>dnab)/p_perms)
names(dists)[2] = sprintf('NVvsRem\np<%.3f', sum(permuteCorr(nmatb, rmatb, p_perms)>dnrb)/p_perms)
names(dists)[3] = sprintf('NVvsPer\np<%.3f', sum(permuteCorr(nmatb, pmatb, p_perms)>dnpb)/p_perms)
names(dists)[4] = sprintf('PervsRem\np<%.3f', sum(permuteCorr(pmatb, rmatb, p_perms)>dprb)/p_perms)
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

# pmatl = cbind(striatum[idxp,4:dim(striatum)[2]], thalamus[idxp,4:dim(thalamus)[2]],
#               gp[idxp,4:dim(gp)[2]])
# rmatl = cbind(striatum[idxr,4:dim(striatum)[2]], thalamus[idxr,4:dim(thalamus)[2]],
#               gp[idxr,4:dim(gp)[2]])
# nmatl = cbind(striatum[idxn,4:dim(striatum)[2]], thalamus[idxn,4:dim(thalamus)[2]],
#               gp[idxn,4:dim(gp)[2]])
# amatl = cbind(striatum[idxa,4:dim(striatum)[2]], thalamus[idxa,4:dim(thalamus)[2]],
#               gp[idxa,4:dim(gp)[2]])

# pmatl = cbind(striatum[idxp,4:dim(striatum)[2]], thalamus[idxp,4:dim(thalamus)[2]])
# rmatl = cbind(striatum[idxr,4:dim(striatum)[2]], thalamus[idxr,4:dim(thalamus)[2]])
# nmatl = cbind(striatum[idxn,4:dim(striatum)[2]], thalamus[idxn,4:dim(thalamus)[2]])
# amatl = cbind(striatum[idxa,4:dim(striatum)[2]], thalamus[idxa,4:dim(thalamus)[2]])

pcovl = cov(pmatl)
rcovl = cov(rmatl)
ncovl = cov(nmatl)
acovl = cov(amatl)

dnal = 1-cor(ncovl[upper.tri(ncovl)], acovl[upper.tri(acovl)], method="spearman")
dnpl = 1-cor(ncovl[upper.tri(ncovl)], pcovl[upper.tri(pcovl)], method="spearman")
dnrl = 1-cor(ncovl[upper.tri(ncovl)], rcovl[upper.tri(rcovl)], method="spearman")
dprl = 1-cor(pcovl[upper.tri(pcovl)], rcovl[upper.tri(rcovl)], method="spearman")

err_dnal = sd(bootstrapCorr(nmatl, amatl, b_perms))
err_dnrl = sd(bootstrapCorr(nmatl, rmatl, b_perms))
err_dnpl = sd(bootstrapCorr(nmatl, pmatl, b_perms))
err_dprl = sd(bootstrapCorr(pmatl, rmatl, b_perms))
dists = c(dnal, dnrl, dnpl, dprl)
err_dists = c(err_dnal, err_dnrl, err_dnpl, err_dprl)
names(dists)[1] = sprintf('NVvsADHD\np<%.3f', sum(permuteCorr(nmatl, amatl, p_perms)>dnal)/p_perms)
names(dists)[2] = sprintf('NVvsRem\np<%.3f', sum(permuteCorr(nmatl, rmatl, p_perms)>dnrl)/p_perms)
names(dists)[3] = sprintf('NVvsPer\np<%.3f', sum(permuteCorr(nmatl, pmatl, p_perms)>dnpl)/p_perms)
names(dists)[4] = sprintf('PervsRem\np<%.3f', sum(permuteCorr(pmatl, rmatl, p_perms)>dprl)/p_perms)
s_dists = sort(dists, index.return=TRUE)
bp = barplot(s_dists$x, main='Follow up', ylim=c(0, 0.7))
error.bar(bp, s_dists$x, err_dists[s_dists$ix])

# now we look at FU-baseline differences
pdelta = pmatl - pmatb
rdelta = rmatl - rmatb
ndelta = nmatl - nmatb
adelta = amatl - amatb
pcovDelta = cov(pdelta)
rcovDelta = cov(rdelta)
ncovDelta = cov(ndelta)
acovDelta = cov(adelta)
dDeltaNA = 1-cor(ncovDelta[upper.tri(ncovDelta)], acovDelta[upper.tri(acovDelta)], method="spearman")
dDeltaNR = 1-cor(ncovDelta[upper.tri(ncovDelta)], rcovDelta[upper.tri(rcovDelta)], method="spearman")
dDeltaNP = 1-cor(ncovDelta[upper.tri(ncovDelta)], pcovDelta[upper.tri(pcovDelta)], method="spearman")
dDeltaPR = 1-cor(pcovDelta[upper.tri(pcovDelta)], rcovDelta[upper.tri(rcovDelta)], method="spearman")
err_dDeltaNA = sd(bootstrapCorr(ndelta, adelta, b_perms))
err_dDeltaNR = sd(bootstrapCorr(ndelta, rdelta, b_perms))
err_dDeltaNP = sd(bootstrapCorr(ndelta, pdelta, b_perms))
err_dDeltaPR = sd(bootstrapCorr(pdelta, rdelta, b_perms))
dists = c(dDeltaNA, dDeltaNR, dDeltaNP, dDeltaPR)
err_dists = c(err_dDeltaNA, err_dDeltaNR, err_dDeltaNP, err_dDeltaPR)
names(dists)[1] = sprintf('NVvsADHD\np<%.3f', sum(permuteCorr(ndelta, adelta, p_perms)>dDeltaNA)/p_perms)
names(dists)[2] = sprintf('NVvsRem\np<%.3f', sum(permuteCorr(ndelta, rdelta, p_perms)>dDeltaNR)/p_perms)
names(dists)[3] = sprintf('NVvsPer\np<%.3f', sum(permuteCorr(ndelta, pdelta, p_perms)>dDeltaNP)/p_perms)
names(dists)[4] = sprintf('PervsRem\np<%.3f', sum(permuteCorr(pdelta, rdelta, p_perms)>dDeltaPR)/p_perms)
s_dists = sort(dists, index.return=TRUE)
bp = barplot(s_dists$x, main='Deltas FU-Baseline', ylim=c(0, 1.2))
error.bar(bp, s_dists$x, err_dists[s_dists$ix])
