striatum = read.csv('~/data/structural/rois_striatumL_QCCIVETlt35_QCSUBePASS.csv')
thalamus= read.csv('~/data/structural/rois_thalamusL_QCCIVETlt35_QCSUBePASS.csv')
gp = read.csv('~/data/structural/rois_gpL_QCCIVETlt35_QCSUBePASS.csv')
cortex = read.csv('~/data/structural/rois_cortexL_QCCIVETlt35_QCSUBePASS.csv')

idxp = striatum$group=="persistent" & striatum$visit=="baseline"
idxr = striatum$group=="remission" & striatum$visit=="baseline"
idxn = striatum$group=="NV" & striatum$visit=="baseline"
# idxa = striatum$group=="ADHD" & striatum$visit=="baseline"
idxa = idxr | idxp

pmat = cbind(striatum[idxp,4:dim(striatum)[2]], thalamus[idxp,4:dim(thalamus)[2]],
             cortex[idxp,4:dim(cortex)[2]], gp[idxp,4:dim(gp)[2]])
rmat = cbind(striatum[idxr,4:dim(striatum)[2]], thalamus[idxr,4:dim(thalamus)[2]],
             cortex[idxr,4:dim(cortex)[2]], gp[idxr,4:dim(gp)[2]])
nmat = cbind(striatum[idxn,4:dim(striatum)[2]], thalamus[idxn,4:dim(thalamus)[2]],
             cortex[idxn,4:dim(cortex)[2]], gp[idxn,4:dim(gp)[2]])
amat = cbind(striatum[idxa,4:dim(striatum)[2]], thalamus[idxa,4:dim(thalamus)[2]],
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

pcorb = cor(pmat)
rcorb = cor(rmat)
ncorb = cor(nmat)
acorb = cor(amat)

dnab = 1-cor(ncorb[upper.tri(ncorb)], acorb[upper.tri(acorb)], method="spearman")
dnpb = 1-cor(ncorb[upper.tri(ncorb)], pcorb[upper.tri(pcorb)], method="spearman")
dnrb = 1-cor(ncorb[upper.tri(ncorb)], rcorb[upper.tri(rcorb)], method="spearman")
dprb = 1-cor(pcorb[upper.tri(pcorb)], rcorb[upper.tri(rcorb)], method="spearman")

#####################

idxp = striatum$group=="persistent" & striatum$visit=="last"
idxr = striatum$group=="remission" & striatum$visit=="last"
idxn = striatum$group=="NV" & striatum$visit=="last"
# idxa = striatum$group=="ADHD" & striatum$visit=="last"
idxa = idxr | idxp

pmat = cbind(striatum[idxp,4:dim(striatum)[2]], thalamus[idxp,4:dim(thalamus)[2]],
             cortex[idxp,4:dim(cortex)[2]], gp[idxp,4:dim(gp)[2]])
rmat = cbind(striatum[idxr,4:dim(striatum)[2]], thalamus[idxr,4:dim(thalamus)[2]],
             cortex[idxr,4:dim(cortex)[2]], gp[idxr,4:dim(gp)[2]])
nmat = cbind(striatum[idxn,4:dim(striatum)[2]], thalamus[idxn,4:dim(thalamus)[2]],
             cortex[idxn,4:dim(cortex)[2]], gp[idxn,4:dim(gp)[2]])
amat = cbind(striatum[idxa,4:dim(striatum)[2]], thalamus[idxa,4:dim(thalamus)[2]],
             cortex[idxa,4:dim(cortex)[2]], gp[idxa,4:dim(gp)[2]])

pcorl = cor(pmat)
rcorl = cor(rmat)
ncorl = cor(nmat)
acorl = cor(amat)

dnal = 1-cor(ncorl[upper.tri(ncorl)], acorl[upper.tri(acorl)], method="spearman")
dnpl = 1-cor(ncorl[upper.tri(ncorl)], pcorl[upper.tri(pcorl)], method="spearman")
dnrl = 1-cor(ncorl[upper.tri(ncorl)], rcorl[upper.tri(rcorl)], method="spearman")
dprl = 1-cor(pcorl[upper.tri(pcorl)], rcorl[upper.tri(rcorl)], method="spearman")

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

b_perms = 1000
p_perms = 1000
err_dnab = sd(bootstrapCorr(ncorb, acorb, b_perms))
err_dnrb = sd(bootstrapCorr(ncorb, rcorb, b_perms))
err_dnpb = sd(bootstrapCorr(ncorb, pcorb, b_perms))
err_dprb = sd(bootstrapCorr(pcorb, rcorb, b_perms))
dists = c(dnab, dnrb, dnpb, dprb)
err_dists = c(err_dnab, err_dnrb, err_dnpb, err_dprb)
names(dists)[1] = sprintf('ADHD (B)\np<%.3f', sum(permuteCorr(ncorb, acorb, b_perms)>dnab)/p_perms)
names(dists)[2] = sprintf('Remission (B)\np<%.3f', sum(permuteCorr(ncorb, rcorb, b_perms)>dnrb)/p_perms)
names(dists)[3] = sprintf('Persistent (B)\np<%.3f', sum(permuteCorr(ncorb, pcorb, b_perms)>dnpb)/p_perms)
names(dists)[4] = sprintf('PvsR (B)\np<%.3f', sum(permuteCorr(pcorb, rcorb, b_perms)>dprb)/p_perms)
s_dists = sort(dists, index.return=TRUE)
par(mfrow=c(1,2))
bp = barplot(s_dists$x, main='Distance from NV (B)', ylim=c(0, 0.7))
error.bar(bp, s_dists$x, err_dists[s_dists$ix])

err_dnal = sd(bootstrapCorr(ncorl, acorl, b_perms))
err_dnrl = sd(bootstrapCorr(ncorl, rcorl, b_perms))
err_dnpl = sd(bootstrapCorr(ncorl, pcorl, b_perms))
err_dprl = sd(bootstrapCorr(pcorl, rcorl, b_perms))
dists = c(dnal, dnrl, dnpl, dprl)
err_dists = c(err_dnal, err_dnrl, err_dnpl, err_dprl)
names(dists)[1] = sprintf('ADHD (FU)\np<%.3f', sum(permuteCorr(ncorl, acorl, b_perms)>dnal)/p_perms)
names(dists)[2] = sprintf('Remission (FU)\np<%.3f', sum(permuteCorr(ncorl, rcorl, b_perms)>dnrl)/p_perms)
names(dists)[3] = sprintf('Persistent (FU)\np<%.3f', sum(permuteCorr(ncorl, pcorl, b_perms)>dnpl)/p_perms)
names(dists)[4] = sprintf('PvsR (FU)\np<%.3f', sum(permuteCorr(pcorl, rcorl, b_perms)>dprl)/p_perms)
s_dists = sort(dists, index.return=TRUE)
bp = barplot(s_dists$x, main='Distance from NV (FU)', ylim=c(0, 0.7))
error.bar(bp, s_dists$x, err_dists[s_dists$ix])