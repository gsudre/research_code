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
nverts = dim(thalamusR)[2]
perm_dists = vector(mode='numeric',length=length(thresh))

for (p in 1:nperms) {
    cat(p,'\n')
    idx = which(group=='NV' & visit=='baseline')
    perm_labels <- sample.int(length(idx), replace = FALSE)
    gidx1 = idx[perm_labels[1:32]]
    es1 = getESfromR(thalamusR[gidx1,], gpR[gidx1,])
    gidx2 = idx[perm_labels[33:48]]
    es2 = getESfromR(thalamusR[gidx2,], gpR[gidx2,])
    gidx3 = idx[perm_labels[49:64]]
    es3 = getESfromR(thalamusR[gidx3,], gpR[gidx3,])
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
          file='~/data/results/structural_v2/perm_dists_NVBaseOnly_thalamusRgpR.txt',
          ncolumns=length(perm_dists),
          append=T)
}

# source('~/research_code/correlation_analysis/compile_last.R')
# for (p in 1:nperms) {
#     cat(p,'\n')
#     idx = which(gfLast$DX=='NV')
#     perm_labels <- sample.int(length(idx), replace = FALSE)
#     gidx1 = idx[perm_labels[1:64]]
#     es1 = getESfromR(thalamusRLast[gidx1,], gpRLast[gidx1,])
#     gidx2 = idx[perm_labels[65:96]]
#     es2 = getESfromR(thalamusRLast[gidx2,], gpRLast[gidx2,])
#     gidx3 = idx[perm_labels[97:128]]
#     es3 = getESfromR(thalamusRLast[gidx3,], gpRLast[gidx3,])
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
#           file='~/data/results/structural_v2/perm_dists_NVAllLastOnly_thalamusRgpR.txt',
#           ncolumns=length(perm_dists),
#           append=T)
# }

# #diff
# source('~/research_code/correlation_analysis/compile_baseline.R')
# source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')
# source('~/research_code/correlation_analysis/compile_last.R')
# for (p in 1:nperms) {
#     cat(p,'\n')
#     bidx = which(gfLast$DX=='NV')
#     perm_labels <- sample.int(length(bidx), replace = FALSE)
#     gidx1 = idx[perm_labels[1:64]]
#     es1 = getESfromR(thalamusRLast[gidx1,] - thalamusRBase[gidx1,], 
#                      gpRLast[gidx1,] - gpRBase[gidx1,])
#     gidx2 = idx[perm_labels[65:96]]
#     es2 = getESfromR(thalamusRLast[gidx2,] - thalamusRBase[gidx2,], 
#                      gpRLast[gidx2,] - gpRBase[gidx2,])
#     gidx3 = idx[perm_labels[97:128]]
#     es3 = getESfromR(thalamusRLast[gidx3,] - thalamusRBase[gidx3,], 
#                      gpRLast[gidx3,] - gpRBase[gidx3,])
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
#           file='~/data/results/structural_v2/perm_dists_NVAllDistOnly_thalamusRgpR.txt',
#           ncolumns=length(perm_dists),
#           append=T)
# }

#delta
# source('~/research_code/correlation_analysis/compile_baseline.R')
# source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')
# source('~/research_code/correlation_analysis/compile_last.R')
# for (p in 1:nperms) {
#     cat(p,'\n')
#     idx = which(gfLast$DX=='NV')
#     perm_labels <- sample.int(length(idx), replace = FALSE)
#     gidx1 = idx[perm_labels[1:64]]
#     es1 = getESfromDeltaInR(thalamusRBase[gidx1,], gpRBase[gidx1,],
#                             thalamusRLast[gidx1,], gpRLast[gidx1,])
#     gidx2 = idx[perm_labels[65:96]]
#     es2 = getESfromDeltaInR(thalamusRBase[gidx2,], gpRBase[gidx2,],
#                             thalamusRLast[gidx2,], gpRLast[gidx2,])
#     gidx3 = idx[perm_labels[97:128]]
#     es3 = getESfromDeltaInR(thalamusRBase[gidx3,], gpRBase[gidx3,],
#                             thalamusRLast[gidx3,], gpRLast[gidx3,])
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
#           file='~/data/results/structural_v2/perm_dists_NVAllDeltaOnly_thalamusRgpR.txt',
#           ncolumns=length(perm_dists),
#           append=T)
# }