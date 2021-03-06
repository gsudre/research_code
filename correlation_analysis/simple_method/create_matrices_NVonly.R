# the goal is to find the maximum separation between the groups when we permute
# the data. in the end we should have one matrix per time, and each matrix is
# ESthresh by nperms

source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')

getESfromR <- function(m1, m2) {
    a = cbind(m1, m2)
    b = cor(a)
    tail = dim(b)[1]
    b = b[1:nverts, (nverts+1):tail]
    # got formula from http://cran.r-project.org/web/packages/compute.es/compute.es.pdf, page 72
    es = 2*b/sqrt(1-b^2)
    return(es)
}

getESfromDeltaInR <- function(m11, m12, m21, m22) {
    # formulas from http://psych.wfu.edu/furr/EffectSizeFormulas.pdf
    b1 = cor(cbind(m11, m12))
    b2 = cor(cbind(m21, m22))
    tail = dim(b1)[1]
    b1 = b1[1:nverts,(nverts+1):tail]
    b2 = b2[1:nverts,(nverts+1):tail]
    z1 = 1/2*log((1+b1)/(1-b1))
    z2 = 1/2*log((1+b2)/(1-b2))
    es = z2 - z1
    return(es)
}

binarize <- function(m, t) {
    bm = matrix(data=F, nrow=dim(m)[1], ncol=dim(m)[2])
    bm[m<t] = F
    bm[m>=t] = T
    return(bm)
}

set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )
nperms = 30
thresh = seq(.2,1,.1)
nverts = dim(thalamusL)[2]
perm_dists = vector(mode='numeric',length=length(thresh))

for (p in 1:nperms) {
    cat(p,'\n')
    idx = which(group=='NV' & visit=='baseline')
    perm_labels <- sample.int(length(idx), replace = FALSE)
    gidx1 = idx[perm_labels[1:32]]
    es1 = getESfromR(thalamusL[gidx1,], cortexL[gidx1,])
    gidx2 = idx[perm_labels[33:48]]
    es2 = getESfromR(thalamusL[gidx2,], cortexL[gidx2,])
    gidx3 = idx[perm_labels[49:64]]
    es3 = getESfromR(thalamusL[gidx3,], cortexL[gidx3,])
    for (i in 1:length(thresh)) {
        bes1 = binarize(abs(es1),thresh[i])
        bes2 = binarize(abs(es2),thresh[i])
        bes3 = binarize(abs(es3),thresh[i])
        d1 = length(setdiff(which(bes1),union(which(bes2),which(bes3))))/sum(bes1)
        d2 = length(setdiff(which(bes2),union(which(bes1),which(bes3))))/sum(bes2)
        d3 = length(setdiff(which(bes3),union(which(bes2),which(bes1))))/sum(bes3)
        perm_dists[i] = max(d1,d2,d3)
    }
    write(perm_dists,
          file='~/data/results/simple/perm_dists_NVOnly_baseline_thalamusLcortexL.txt',
          ncolumns=length(perm_dists),
          append=T)
}

# diff
# for (p in 1:nperms) {
#     cat(p,'\n')
#     idx = which(group=='NV' & visit=='baseline')
#     perm_labels <- sample.int(length(idx), replace = FALSE)
#     gidx1 = idx[perm_labels[1:32]]
#     es1 = getESfromR(thalamusL[gidx1+1,] - thalamusL[gidx1,], 
#                      cortexL[gidx1+1,] - cortexL[gidx1,])
#     gidx2 = idx[perm_labels[33:48]]
#     es2 = getESfromR(thalamusL[gidx2+1,] - thalamusL[gidx2,], 
#                      cortexL[gidx2+1,] - cortexL[gidx2,])
#     gidx3 = idx[perm_labels[49:64]]
#     es3 = getESfromR(thalamusL[gidx3+1,] - thalamusL[gidx3,], 
#                      cortexL[gidx3+1,] - cortexL[gidx3,])
    
#     for (i in 1:length(thresh)) {
#         bes1 = binarize(abs(es1),thresh[i])
#         bes2 = binarize(abs(es2),thresh[i])
#         bes3 = binarize(abs(es3),thresh[i])
#         d1 = length(setdiff(which(bes1),union(which(bes2),which(bes3))))/sum(bes1)
#         d2 = length(setdiff(which(bes2),union(which(bes1),which(bes3))))/sum(bes2)
#         d3 = length(setdiff(which(bes3),union(which(bes2),which(bes1))))/sum(bes3)
#         perm_dists[i] = max(d1,d2,d3)
#     }
#     write(perm_dists,
#           file='~/data/results/structural_v2/perm_dists_NVOnly_diff_thalamusLcortexL.txt',
#           ncolumns=length(perm_dists),
#           append=T)
# }

# delta
# for (p in 1:nperms) {
#     cat(p,'\n')
#     idx = which(group=='NV' & visit=='baseline')
#     perm_labels <- sample.int(length(idx), replace = FALSE)
#     gidx1 = idx[perm_labels[1:32]]
#     es1 = getESfromDeltaInR(thalamusL[gidx1,], striatumR[gidx1,],
#                             thalamusL[gidx1+1,], striatumR[gidx1+1,])
#     gidx2 = idx[perm_labels[33:48]]
#     es2 = getESfromDeltaInR(thalamusL[gidx2,], striatumR[gidx2,],
#                             thalamusL[gidx2+1,], striatumR[gidx2+1,])
#     gidx3 = idx[perm_labels[49:64]]
#     es3 = getESfromDeltaInR(thalamusL[gidx3,], striatumR[gidx3,],
#                             thalamusL[gidx3+1,], striatumR[gidx3+1,])
#     
#     for (i in 1:length(thresh)) {
#         bes1 = binarize(abs(es1),thresh[i])
#         bes2 = binarize(abs(es2),thresh[i])
#         bes3 = binarize(abs(es3),thresh[i])
#         d1 = length(setdiff(which(bes1),union(which(bes2),which(bes3))))/sum(bes1)
#         d2 = length(setdiff(which(bes2),union(which(bes1),which(bes3))))/sum(bes2)
#         d3 = length(setdiff(which(bes3),union(which(bes2),which(bes1))))/sum(bes3)
#         perm_dists[i] = max(d1,d2,d3)
#     }
#     write(perm_dists,
#           file='~/data/results/structural_v2/perm_dists_NVOnly_delta_thalamusLcortexL.txt',
#           ncolumns=length(perm_dists),
#           append=T)
# }