out_mask='~/data/tmp/perms7/perm'
data_dir = '~/data/dti/'
nii_template = 'persistentVSremitted_FA_skeletonised.nii.gz'
gf = read.csv('~/tmp/FINAL_TSA_allClean149.csv')
nperms = 20
brain_data = read.table('~/data/dti/persistentVSremitted_FA_skeletonised.txt')
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
# tmp = as.factor(tmp)
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
    for (v in 1:nvoxels) {
        # CHECK THIS FOR EVERY MODEL!
        stats[v] = cor.test(data[v,], randtmp)$statistic
    }
    out[,4] = stats
    fname = sprintf('%s_%s-%05f', out_mask, Sys.info()["nodename"], runif(1, 1, 99999))
    write.table(out, file=sprintf('%s.txt', fname), col.names=F, row.names=F)
    system(sprintf('cat %s.txt | 3dUndump -master %s/%s -datum float -prefix %s.nii.gz -overwrite -',
                   fname, data_dir, nii_template, fname), wait=T)
    system(sprintf('fslmaths %s.nii.gz -tfce 2 1 26 %s_tfce.nii.gz', fname, fname), wait=T)
    system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s/mean_FA_skeleton_mask.nii.gz %s_tfce.nii.gz',
                   fname, data_dir, fname), wait=T)
    system(sprintf('rm %s.nii.gz %s_tfce.nii.gz', fname, fname), wait=T)
}
