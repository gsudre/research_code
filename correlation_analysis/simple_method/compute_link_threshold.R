# the goal is to find the maximum separation between the groups when we permute
# the data. in the end we should have one matrix per time, and each matrix is
# ESthresh by nperms

source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')
set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )
nperms = 10
thresh=.5
nverts = dim(thalamusR)[2]

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

#### baseline or last
v = 'baseline'
for (p in 1:nperms) {
    cat(p,'\n')
    idx = which(visit==v)
    perm_labels <- sample.int(length(idx), replace = FALSE)
    perm_idx = idx[perm_labels]
    es = getESfromR(thalamusR[idx,], gpR[perm_idx,])
    bes = binarize(abs(es),thresh)
    perm_link = max(rowSums(es))/dim(es)[2]
    write(perm_link,
          file=sprintf('~/data/results/structural_v2/perm_conn_thresh%0.2f_thalamusRgpR_%s.txt',
                       thresh, v),
          append=T)
}


#### diff
# for (p in 1:nperms) {
#     cat(p,'\n')
#     idx = which(visit=='baseline')
#     perm_labels <- sample.int(length(idx), replace = FALSE)
#     perm_idx = idx[perm_labels]
#     es = getESfromR(thalamusR[idx+1,] - thalamusR[idx,], 
#                     gpR[perm_idx+1,] - gpR[perm_idx,])
#     bes = binarize(abs(es),thresh)
#     perm_link = max(rowSums(es))/dim(es)[2]
#     write(perm_link,
#           file=sprintf('~/data/results/structural_v2/perm_conn_thresh%0.2f_thalamusRgpR_diff.txt', thresh),
#           append=T)
# }

#### delta
# for (p in 1:nperms) {
#     cat(p,'\n')
#     idx = which(visit=='baseline')
#     perm_labels <- sample.int(length(idx), replace = FALSE)
#     perm_idx = idx[perm_labels]
#     es = getESfromDeltaInR(thalamusR[idx,], gpR[perm_idx,],
#                            thalamusR[idx+1,], gpR[perm_idx+1,])
#     bes = binarize(abs(es),thresh)
#     perm_link = max(rowSums(es))/dim(es)[2]
#     write(perm_link,
#           file=sprintf('~/data/results/structural_v2/perm_conn_thresh%0.2f_thalamusRgpR_delta.txt', thresh),
#           append=T)
# }