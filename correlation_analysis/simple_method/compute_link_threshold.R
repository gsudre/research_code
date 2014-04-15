# Finds the maximum connectiviy between a voxel in the thalamus and vertices in the other brain region. It appends to a text file so that we can run multiple instances of this script at the same time.

source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')
set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )
nperms = 10
thresh = .5
hemi = 'L'
other = 'cortex'
time = 'diff'
outdir = '~/data/results/simple/'
fname = sprintf('%s/perm_conn_thresh%0.2f_%s%sthalamus%s_%s.txt',
                outdir,thresh,other,hemi,hemi,time)
# fname = sprintf('%s/perm_conn_thresh%0.2f_thalamus%s%s%s_%s.txt',
                # outdir,thresh,hemi,other,hemi,time)

eval(parse(text=sprintf('thalamus = thalamus%s', hemi)))
eval(parse(text=sprintf('target = %s%s', other, hemi)))
nverts = dim(thalamus)[2]

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

if (time=='baseline' || time=='last') {
    for (p in 1:nperms) {
        cat(p,'\n')
        idx = which(visit==time)
        perm_labels <- sample.int(length(idx), replace = FALSE)
        perm_idx = idx[perm_labels]
        es = getESfromR(thalamus[idx,], target[perm_idx,])
        bes = binarize(abs(es),thresh)
        # perm_link = max(rowSums(es))/dim(es)[2]
        perm_link = max(colSums(es))/dim(es)[1]
        write(perm_link, file=fname, append=T)
    }
} else if (time=='diff') {
    for (p in 1:nperms) {
        cat(p,'\n')
        idx = which(visit=='baseline')
        perm_labels <- sample.int(length(idx), replace = FALSE)
        perm_idx = idx[perm_labels]
        es = getESfromR(thalamus[idx+1,] - thalamus[idx,], 
                        target[perm_idx+1,] - target[perm_idx,])
        bes = binarize(abs(es),thresh)
        # perm_link = max(rowSums(es))/dim(es)[2]
        perm_link = max(colSums(es))/dim(es)[1]
        write(perm_link, file=fname, append=T)
    }
} else if (time=='delta') {
    for (p in 1:nperms) {
        cat(p,'\n')
        idx = which(visit=='baseline')
        perm_labels <- sample.int(length(idx), replace = FALSE)
        perm_idx = idx[perm_labels]
        es = getESfromDeltaInR(thalamus[idx,], target[perm_idx,],
                               thalamus[idx+1,], target[perm_idx+1,])
        bes = binarize(abs(es),thresh)
        # perm_link = max(rowSums(es))/dim(es)[2]
        perm_link = max(colSums(es))/dim(es)[1]
        write(perm_link, file=fname, append=T)
    }
}