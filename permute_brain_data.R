out_mask='~/data/tmp/perms/perm'
gf = read.csv('~/tmp/FINAL_TSA_allClean149.csv')
nperms = 3
tmp = gf$SX_inattb
brain_data = read.table('~/data/dti/all_FA_skeleton.txt')
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
    fname = sprintf('%s_%s-%05f.RData', out_mask, Sys.info()["nodename"], runif(1, 1, 99999))
    write.table(out, file=fname, col.names=F, row.names=F)
}
