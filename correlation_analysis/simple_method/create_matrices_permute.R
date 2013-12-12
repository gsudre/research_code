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
    bm = m    
    bm[m<t] = 0
    bm[m>=t] = 1
    return(bm)
}

set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )
nperms = 30
thresh = seq(.2,1,.1)
nverts = dim(thalamusR)[2]
perm_dists = vector(mode='numeric',length=length(thresh))

#### baseline or last
v = 'baseline'
for (p in 1:nperms) {
    cat(p,'\n')
    idx = which(visit==v)
    perm_labels <- sample.int(length(idx), replace = FALSE)
    gidx1 = idx[perm_labels[1:64]]
    es1 = getESfromR(thalamusR[gidx1,], striatumR[gidx1,])
    gidx2 = idx[perm_labels[65:96]]
    es2 = getESfromR(thalamusR[gidx2,], striatumR[gidx2,])
    gidx3 = idx[perm_labels[97:128]]
    es3 = getESfromR(thalamusR[gidx3,], striatumR[gidx3,])
    for (i in 1:length(thresh)) {
        bes1 = binarize(abs(es1),thresh[i])
        bes2 = binarize(abs(es2),thresh[i])
        bes3 = binarize(abs(es3),thresh[i])
        d1 = sum((bes1-bes2-bes3)==1)/sum(bes1==1)
        d2 = sum((bes2-bes1-bes3)==1)/sum(bes2==1)
        d3 = sum((bes3-bes2-bes1)==1)/sum(bes3==1)
        perm_dists[i] = max(d1,d2,d3)
    }
    write(perm_dists,
          file=sprintf('~/data/results/structural_v2/perm_dists_thalamusRstriatumR_%s.txt', v),
          ncolumns=length(perm_dists),
          append=T)
}

#### diff
# for (p in 1:nperms) {
#     cat(p,'\n')
#     idx = which(visit=='baseline')
#     # we assume that the last visit of a subject comes right after the baseline
#     perm_labels <- sample.int(length(idx), replace = FALSE)
#     gidx1 = idx[perm_labels[1:64]]
#     es1 = getESfromR(thalamusR[gidx1+1,] - thalamusR[gidx1,], 
#                      striatumR[gidx1+1,] - striatumR[gidx1,])
#     gidx2 = idx[perm_labels[65:96]]
#     es2 = getESfromR(thalamusR[gidx2+1,] - thalamusR[gidx2,],
#                      striatumR[gidx2+1,] - striatumR[gidx2,])
#     gidx3 = idx[perm_labels[97:128]]
#     es3 = getESfromR(thalamusR[gidx3+1,] - thalamusR[gidx3,], 
#                      striatumR[gidx3+1,] - striatumR[gidx3,])
#     for (i in 1:length(thresh)) {
#         bes1 = binarize(abs(es1),thresh[i])
#         bes2 = binarize(abs(es2),thresh[i])
#         bes3 = binarize(abs(es3),thresh[i])
#         d1 = sum((bes1-bes2-bes3)==1)/sum(bes1==1)
#         d2 = sum((bes2-bes1-bes3)==1)/sum(bes2==1)
#         d3 = sum((bes3-bes2-bes1)==1)/sum(bes3==1)
#         perm_dists[i] = max(d1,d2,d3)
#     }
#     write(perm_dists,
#           file='~/data/results/structural_v2/perm_dists_thalamusRstriatumR_diff.txt',
#           ncolumns=length(perm_dists),
#           append=T)
# }

#### delta
# for (p in 1:nperms) {
#     cat(p,'\n')
#         idx = which(visit=='baseline')
#         perm_labels <- sample.int(length(idx), replace = FALSE)
#         gidx1 = idx[perm_labels[1:64]]
#         es1 = getESfromDeltaInR(thalamusR[gidx1,], striatumR[gidx1,],
#                                 thalamusR[gidx1+1,], striatumR[gidx1+1,])
#         gidx2 = idx[perm_labels[65:96]]
#         es2 = getESfromDeltaInR(thalamusR[gidx2,], striatumR[gidx2,],
#                                 thalamusR[gidx2+1,], striatumR[gidx2+1,])
#         gidx3 = idx[perm_labels[97:128]]
#         es3 = getESfromDeltaInR(thalamusR[gidx3,], striatumR[gidx3,],
#                                 thalamusR[gidx3+1,], striatumR[gidx3+1,])
#     for (i in 1:length(thresh)) {
#         bes1 = binarize(abs(es1),thresh[i])
#         bes2 = binarize(abs(es2),thresh[i])
#         bes3 = binarize(abs(es3),thresh[i])
#         d1 = sum((bes1-bes2-bes3)==1)/sum(bes1==1)
#         d2 = sum((bes2-bes1-bes3)==1)/sum(bes2==1)
#         d3 = sum((bes3-bes2-bes1)==1)/sum(bes3==1)
#         perm_dists[i] = max(d1,d2,d3)
#     }
#     write(perm_dists,
#           file='~/data/results/structural_v2/perm_dists_thalamusRstriatumR_delta.txt',
#           ncolumns=length(perm_dists),
#           append=T)
# }