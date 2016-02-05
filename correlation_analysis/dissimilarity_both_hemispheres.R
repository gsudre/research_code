striatumL = read.csv('~/data/structural/roisSum_striatumL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')
thalamusL= read.csv('~/data/structural/roisSum_thalamusL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')
gpL = read.csv('~/data/structural/roisSum_gpL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')
cortexL = read.csv('~/data/structural/roisSum_cortexL_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')
striatumR = read.csv('~/data/structural/roisSum_striatumR_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')
thalamusR= read.csv('~/data/structural/roisSum_thalamusR_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')
gpR = read.csv('~/data/structural/roisSum_gpR_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')
cortexR = read.csv('~/data/structural/roisSum_cortexR_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT.csv')

# striatum = cbind(striatumL, striatumR[,4:dim(striatumR)[2]])
# gp = cbind(gpL, gpR[,4:dim(gpR)[2]])
# thalamus = cbind(thalamusL, thalamusR[,4:dim(thalamusR)[2]])
# cortex = cbind(cortexL, cortexR[,4:dim(cortexR)[2]])

permuteCorr <- function(data1L, data2L, data1R, data2R, nperms) 
{
    ds <- vector(mode = "numeric", length = nperms) 
    all_dataL = rbind(data1L, data2L)
    all_dataR = rbind(data1R, data2R)
    n1 = dim(data1L)[1]
    n2 = dim(data2L)[1]
    for (i in 1:nperms) {
        perm_labels <- sample.int(dim(all_dataL)[1], replace = FALSE)
        perm_dataL <- all_dataL[perm_labels, ]
        perm_dataR <- all_dataR[perm_labels, ]
        pmat1L = perm_dataL[1:n1, ]
        pmat2L = perm_dataL[(n1+1):(n1+n2), ]
        pmat1R = perm_dataR[1:n1, ]
        pmat2R = perm_dataR[(n1+1):(n1+n2), ]
        cor1L = cor(pmat1L)
        cor2L = cor(pmat2L)
        cor1R = cor(pmat1R)
        cor2R = cor(pmat2R)
        cor1 = c(cor1L[upper.tri(cor1L)],cor1R[upper.tri(cor1R)])
        cor2 = c(cor2L[upper.tri(cor2L)],cor2R[upper.tri(cor2R)])
        ds[i] = 1-cor(cor1, cor2, method="spearman")
    }
    return(ds)
}

# bootstrapCorr <- function(fixed_data, data, nperms) 
# {
#     ds <- vector(mode = "numeric", length = nperms) 
#     cor1 = cor(fixed_data)
#     for (i in 1:nperms) {
#         perm_labels <- sample.int(dim(data)[1], replace = TRUE)
#         perm_data <- data[perm_labels, ]
#         cor2 = cor(perm_data)
#         ds[i] = 1-cor(cor1[upper.tri(cor1)], cor2[upper.tri(cor2)], method="spearman")
#     }
#     return(ds)
# }

error.bar <- function(x, y, upper, lower=upper, length=0.1,...){
    if(length(x) != length(y) | length(y) !=length(lower) | length(lower) != length(upper))
        stop("vectors must be same length")
    arrows(x,y+upper, x, y-lower, angle=90, code=3, length=length, ...)
}

idxp = striatum$group=="persistent" & striatum$visit=="baseline"
idxr = striatum$group=="remission" & striatum$visit=="baseline"
idxn = striatum$group=="NV" & striatum$visit=="baseline"
idxa = idxr | idxp

pmatbL = cbind(striatumL[idxp,4:dim(striatumL)[2]], thalamusL[idxp,4:dim(thalamusL)[2]],
              gpL[idxp,4:dim(gpL)[2]])
rmatbL = cbind(striatumL[idxr,4:dim(striatumL)[2]], thalamusL[idxr,4:dim(thalamusL)[2]],
              gpL[idxr,4:dim(gpL)[2]])
nmatbL = cbind(striatumL[idxn,4:dim(striatumL)[2]], thalamusL[idxn,4:dim(thalamusL)[2]],
              gpL[idxn,4:dim(gpL)[2]])
amatbL = cbind(striatumL[idxa,4:dim(striatumL)[2]], thalamusL[idxa,4:dim(thalamusL)[2]],
              gpL[idxa,4:dim(gpL)[2]])

pcorbL = cor(pmatbL)
rcorbL = cor(rmatbL)
ncorbL = cor(nmatbL)
acorbL = cor(amatbL)

pmatbR = cbind(striatumR[idxp,4:dim(striatumR)[2]], thalamusR[idxp,4:dim(thalamusR)[2]],
               gpR[idxp,4:dim(gpR)[2]])
rmatbR = cbind(striatumR[idxr,4:dim(striatumR)[2]], thalamusR[idxr,4:dim(thalamusR)[2]],
               gpR[idxr,4:dim(gpR)[2]])
nmatbR = cbind(striatumR[idxn,4:dim(striatumR)[2]], thalamusR[idxn,4:dim(thalamusR)[2]],
               gpR[idxn,4:dim(gpR)[2]])
amatbR = cbind(striatumR[idxa,4:dim(striatumR)[2]], thalamusR[idxa,4:dim(thalamusR)[2]],
               gpR[idxa,4:dim(gpR)[2]])

pcorbR = cor(pmatbR)
rcorbR = cor(rmatbR)
ncorbR = cor(nmatbR)
acorbR = cor(amatbR)

pcorb = c(pcorbL[upper.tri(pcorbL)],pcorbR[upper.tri(pcorbR)])
rcorb = c(rcorbL[upper.tri(rcorbL)],rcorbR[upper.tri(rcorbR)])
ncorb = c(ncorbL[upper.tri(ncorbL)],ncorbR[upper.tri(ncorbR)])
acorb = c(acorbL[upper.tri(acorbL)],acorbR[upper.tri(acorbR)])

dnab = 1-cor(ncorb, acorb, method="spearman")
dnpb = 1-cor(ncorb, pcorb, method="spearman")
dnrb = 1-cor(ncorb, rcorb, method="spearman")
dprb = 1-cor(pcorb, rcorb, method="spearman")

# b_perms = 1000
p_perms = 1000
# err_dnab = sd(bootstrapCorr(nmatb, amatb, b_perms))
# err_dnrb = sd(bootstrapCorr(nmatb, rmatb, b_perms))
# err_dnpb = sd(bootstrapCorr(nmatb, pmatb, b_perms))
# err_dprb = sd(bootstrapCorr(pmatb, rmatb, b_perms))
dists = c(dnab, dnrb, dnpb, dprb)
# err_dists = c(err_dnab, err_dnrb, err_dnpb, err_dprb)
names(dists)[1] = sprintf('NVvsADHD\np<%.3f', sum(permuteCorr(nmatbL, amatbL, nmatbR, amatbR, p_perms)>dnab)/p_perms)
names(dists)[2] = sprintf('NVvsRem\np<%.3f', sum(permuteCorr(nmatbL, rmatbL, nmatbR, rmatbR, p_perms)>dnrb)/p_perms)
names(dists)[3] = sprintf('NVvsPer\np<%.3f', sum(permuteCorr(nmatbL, pmatbL, nmatbR, pmatbR, p_perms)>dnpb)/p_perms)
names(dists)[4] = sprintf('PervsRem\np<%.3f', sum(permuteCorr(pmatbL, rmatbL, pmatbR, rmatbR, p_perms)>dprb)/p_perms)
s_dists = sort(dists, index.return=TRUE)
par(mfrow=c(1,3))
bp = barplot(s_dists$x, main='Baseline', ylim=c(0, 0.7))
# error.bar(bp, s_dists$x, err_dists[s_dists$ix])

#####################

idxp = striatum$group=="persistent" & striatum$visit=="last"
idxr = striatum$group=="remission" & striatum$visit=="last"
idxn = striatum$group=="NV" & striatum$visit=="last"
idxa = idxr | idxp

pmatlL = cbind(striatumL[idxp,4:dim(striatumL)[2]], thalamusL[idxp,4:dim(thalamusL)[2]],
               gpL[idxp,4:dim(gpL)[2]])
rmatlL = cbind(striatumL[idxr,4:dim(striatumL)[2]], thalamusL[idxr,4:dim(thalamusL)[2]],
               gpL[idxr,4:dim(gpL)[2]])
nmatlL = cbind(striatumL[idxn,4:dim(striatumL)[2]], thalamusL[idxn,4:dim(thalamusL)[2]],
               gpL[idxn,4:dim(gpL)[2]])
amatlL = cbind(striatumL[idxa,4:dim(striatumL)[2]], thalamusL[idxa,4:dim(thalamusL)[2]],
               gpL[idxa,4:dim(gpL)[2]])

pcorlL = cor(pmatlL)
rcorlL = cor(rmatlL)
ncorlL = cor(nmatlL)
acorlL = cor(amatlL)

pmatlR = cbind(striatumR[idxp,4:dim(striatumR)[2]], thalamusR[idxp,4:dim(thalamusR)[2]],
               gpR[idxp,4:dim(gpR)[2]])
rmatlR = cbind(striatumR[idxr,4:dim(striatumR)[2]], thalamusR[idxr,4:dim(thalamusR)[2]],
               gpR[idxr,4:dim(gpR)[2]])
nmatlR = cbind(striatumR[idxn,4:dim(striatumR)[2]], thalamusR[idxn,4:dim(thalamusR)[2]],
               gpR[idxn,4:dim(gpR)[2]])
amatlR = cbind(striatumR[idxa,4:dim(striatumR)[2]], thalamusR[idxa,4:dim(thalamusR)[2]],
               gpR[idxa,4:dim(gpR)[2]])

pcorlR = cor(pmatlR)
rcorlR = cor(rmatlR)
ncorlR = cor(nmatlR)
acorlR = cor(amatlR)

pcorl = c(pcorlL[upper.tri(pcorlL)],pcorlR[upper.tri(pcorlR)])
rcorl = c(rcorlL[upper.tri(rcorlL)],rcorlR[upper.tri(rcorlR)])
ncorl = c(ncorlL[upper.tri(ncorlL)],ncorlR[upper.tri(ncorlR)])
acorl = c(acorlL[upper.tri(acorlL)],acorlR[upper.tri(acorlR)])

dnal = 1-cor(ncorl, acorl, method="spearman")
dnpl = 1-cor(ncorl, pcorl, method="spearman")
dnrl = 1-cor(ncorl, rcorl, method="spearman")
dprl = 1-cor(pcorl, rcorl, method="spearman")

# b_perms = 1000
p_perms = 1000
# err_dnab = sd(bootstrapCorr(nmatb, amatb, b_perms))
# err_dnrb = sd(bootstrapCorr(nmatb, rmatb, b_perms))
# err_dnpb = sd(bootstrapCorr(nmatb, pmatb, b_perms))
# err_dprb = sd(bootstrapCorr(pmatb, rmatb, b_perms))
dists = c(dnal, dnrl, dnpl, dprl)
# err_dists = c(err_dnab, err_dnrb, err_dnpb, err_dprb)
names(dists)[1] = sprintf('NVvsADHD\np<%.3f', sum(permuteCorr(nmatlL, amatlL, nmatlR, amatlR, p_perms)>dnal)/p_perms)
names(dists)[2] = sprintf('NVvsRem\np<%.3f', sum(permuteCorr(nmatlL, rmatlL, nmatlR, rmatlR, p_perms)>dnrl)/p_perms)
names(dists)[3] = sprintf('NVvsPer\np<%.3f', sum(permuteCorr(nmatlL, pmatlL, nmatlR, pmatlR, p_perms)>dnpl)/p_perms)
names(dists)[4] = sprintf('PervsRem\np<%.3f', sum(permuteCorr(pmatlL, rmatlL, pmatlR, rmatlR, p_perms)>dprl)/p_perms)
s_dists = sort(dists, index.return=TRUE)
bp = barplot(s_dists$x, main='Follow-uP', ylim=c(0, 0.7))
# error.bar(bp, s_dists$x, err_dists[s_dists$ix])

# now we look at FU-baseline differences
pdeltaL = pmatlL - pmatbL
rdeltaL = rmatlL - rmatbL
ndeltaL = nmatlL - nmatbL
adeltaL = amatlL - amatbL
pcorDeltaL = cor(pdeltaL)
rcorDeltaL = cor(rdeltaL)
ncorDeltaL = cor(ndeltaL)
acorDeltaL = cor(adeltaL)
pdeltaR = pmatlR - pmatbR
rdeltaR = rmatlR - rmatbR
ndeltaR = nmatlR - nmatbR
adeltaR = amatlR - amatbR
pcorDeltaR = cor(pdeltaR)
rcorDeltaR = cor(rdeltaR)
ncorDeltaR = cor(ndeltaR)
acorDeltaR = cor(adeltaR)
ncorDelta = c(ncorDeltaL[upper.tri(ncorDeltaL)],ncorDeltaR[upper.tri(ncorDeltaR)])
pcorDelta = c(pcorDeltaL[upper.tri(pcorDeltaL)],pcorDeltaR[upper.tri(pcorDeltaR)])
rcorDelta = c(rcorDeltaL[upper.tri(rcorDeltaL)],rcorDeltaR[upper.tri(rcorDeltaR)])
acorDelta = c(acorDeltaL[upper.tri(acorDeltaL)],acorDeltaR[upper.tri(acorDeltaR)])
dDeltaNA = 1-cor(ncorDelta, acorDelta, method="spearman")
dDeltaNR = 1-cor(ncorDelta, rcorDelta, method="spearman")
dDeltaNP = 1-cor(ncorDelta, pcorDelta, method="spearman")
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
