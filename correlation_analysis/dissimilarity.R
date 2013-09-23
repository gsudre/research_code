striatum = read.csv('~/data/structural/rois_striatumR.csv')
thalamus= read.csv('~/data/structural/rois_thalamusR.csv')
gp = read.csv('~/data/structural/rois_gpR.csv')
cortex = read.csv('~/data/structural/rois_cortexR.csv')

idxp = striatumR$group=="persistent" & striatumR$visit=="baseline"
idxr = striatumR$group=="remission" & striatumR$visit=="baseline"
idxn = striatumR$group=="NV" & striatumR$visit=="baseline"
idxa = striatumR$group=="ADHD" & striatumR$visit=="baseline"

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

#####################

idxp = striatumR$group=="persistent" & striatumR$visit=="last"
idxr = striatumR$group=="remission" & striatumR$visit=="last"
idxn = striatumR$group=="NV" & striatumR$visit=="last"
idxa = striatumR$group=="ADHD" & striatumR$visit=="last"

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

dnnl = 1-cor(ncorb[upper.tri(ncorb)], ncorl[upper.tri(ncorl)], method="spearman")
dnal = 1-cor(ncorb[upper.tri(ncorb)], acorl[upper.tri(acorl)], method="spearman")
dnpl = 1-cor(ncorb[upper.tri(ncorb)], pcorl[upper.tri(pcorl)], method="spearman")
dnrl = 1-cor(ncorb[upper.tri(ncorb)], rcorl[upper.tri(rcorl)], method="spearman")

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
err_dnab = sd(bootstrapCorr(ncorb, acorb, b_perms))
err_dnrb = sd(bootstrapCorr(ncorb, ncorb, b_perms))
err_dnpb = sd(bootstrapCorr(ncorb, pcorb, b_perms))
err_dnnl = sd(bootstrapCorr(ncorb, ncorl, b_perms))
err_dnal = sd(bootstrapCorr(ncorb, acorl, b_perms))
err_dnpl = sd(bootstrapCorr(ncorb, pcorl, b_perms))
err_dnrl = sd(bootstrapCorr(ncorb, rcorl, b_perms))

dists = c(dnab, dnrb, dnpb, dnnl, dnal, dnpl, dnrl)
err_dists = c(err_dnab, err_dnrb, err_dnpb, err_dnnl, err_dnal, err_dnpl, err_dnrl)

p_perms = 1000
names(dists)[1] = sprintf('ADHD (B)\np<%.3f', sum(permuteCorr(ncorb, acorb, b_perms)>dnab)/p_perms)
names(dists)[2] = sprintf('Remission (B)\np<%.3f', sum(permuteCorr(ncorb, rcorb, b_perms)>dnrb)/p_perms)
names(dists)[3] = sprintf('Persistent (B)\np<%.3f', sum(permuteCorr(ncorb, pcorb, b_perms)>dnpb)/p_perms)
names(dists)[4] = sprintf('NV (FU)\np<%.3f', sum(permuteCorr(ncorb, ncorl, b_perms)>dnnl)/p_perms)
names(dists)[5] = sprintf('ADHD (FU)\np<%.3f', sum(permuteCorr(ncorb, acorl, b_perms)>dnal)/p_perms)
names(dists)[6] = sprintf('Persistent (FU)\np<%.3f', sum(permuteCorr(ncorb, pcorl, b_perms)>dnpl)/p_perms)
names(dists)[7] = sprintf('Remission (FU)\np<%.3f', sum(permuteCorr(ncorb, rcorl, b_perms)>dnrl)/p_perms)

s_dists = sort(dists, index.return=TRUE)
bp = barplot(s_dists$x, main='Distance from NV (B)', ylim=c(0, 0.5))
error.bar(bp, s_dists$x, err_dists[s_dists$ix])