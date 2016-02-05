nperms = 100
dists = vector(mode="numeric", length=nperms)
for (p in 1:nperms) {
    cat('Working on perm', p, '/', nperms, '\n')
    idx <- sample.int(length(group)/2, replace = FALSE)
    
    mygroup = group[idx_base]
    data = thalamusR[idx_base,]
    seed = gpR[idx_base,]
    seed = rowMeans(seed)
    nverts = dim(data)[2]
    ngroup1 = sum(mygroup==mygroup[1])
    ngroup2 = length(mygroup) - ngroup1
    gidx1 = 1:ngroup1
    gidx2 = (ngroup1+1):(ngroup1+ngroup2)
    msapprox_base = array(dim=c(nverts, 2))
    for (i in 1:nverts) { 
        msapprox_base[i, 1] = cor(seed[idx[gidx1]], data[idx[gidx1], i])
        msapprox_base[i, 2] = cor(seed[idx[gidx2]], data[idx[gidx2], i])
    }
    
    mygroup = group[idx_last]
    data = thalamusR[idx_last,]
    seed = gpR[idx_last,]
    seed = rowMeans(seed)
    msapprox_last = array(dim=c(nverts, 2))
    for (i in 1:nverts) { 
        msapprox_last[i, 1] = cor(seed[idx[gidx1]], data[idx[gidx1], i])
        msapprox_last[i, 2] = cor(seed[idx[gidx2]], data[idx[gidx2], i])
    }
    
    ms_delta = msapprox_last - msapprox_base
    dists[p] = 1 - cor(ms_delta[,1], ms_delta[,2], method="spearman")
}

mygroup = group[idx_base]
data = thalamusR[idx_base,]
seed = gpR[idx_base,]
seed = rowMeans(seed)
nverts = dim(data)[2]
gidx1 = mygroup==unique(mygroup)[1]
gidx2 = mygroup==unique(mygroup)[2]
msapprox_base = array(dim=c(nverts, 2))
for (i in 1:nverts) { 
    msapprox_base[i, 1] = cor(seed[gidx1], data[gidx1, i])
    msapprox_base[i, 2] = cor(seed[gidx2], data[gidx2, i])
}
mygroup = group[idx_last]
data = thalamusR[idx_last,]
seed = gpR[idx_last,]
seed = rowMeans(seed)
msapprox_last = array(dim=c(nverts, 2))
for (i in 1:nverts) { 
    msapprox_last[i, 1] = cor(seed[gidx1], data[gidx1, i])
    msapprox_last[i, 2] = cor(seed[gidx2], data[gidx2, i])
}
ms_delta = msapprox_last - msapprox_base
theDist = 1 - cor(ms_delta[,1], ms_delta[,2], method="spearman")