out_mask='~/data/tmp/perms/perm'
gf = read.csv('~/tmp/FINAL_TSA_allClean149.csv')
nperms = 20
brain_data = read.table('~/data/dti/perVSrem_FA_skeleton.txt')
data = gf$SX_inattb
nsubj = dim(gf)[1]
tmp = vector()
for (i in 1:nsubj) {
    if (gf[i,]$DX_GROUP=='persistent') {
        tmp = c(tmp, data[i])
    }
}
for (i in 1:nsubj) {
    if (gf[i,]$DX_GROUP=='remitted') {
        tmp = c(tmp, data[i])
    }
}
# tmp = gf$SX_inattb

###
set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )
out = brain_data[,1:4]
data = as.matrix(brain_data[,4:dim(brain_data)[2]])
nvoxels = dim(data)[1]
stats = vector(length=nvoxels, mode="numeric")
for (p in 1:nperms) {
    print(sprintf('perm %d',p))
    perm_labels <- sample.int(length(tmp), replace = FALSE)
    randtmp = tmp[perm_labels]
    for (v in 1:dim(data)[1]) {
        fit = lm(data[v,]~randtmp)
        # CHECK THIS FOR EVERY MODEL!
        stats[v] = summary(fit)$coefficients[2,3]
    }
    out[,4] = stats
    fname = sprintf('%s_%s-%05f.txt', out_mask, Sys.info()["nodename"], runif(1, 1, 99999))
    write.table(out, file=fname, col.names=F, row.names=F)
}
