out_dir='~/data/results/tfce/'
data_dir = '~/data/dti/'
# nii_template = 'all_FA_skeletonised.nii.gz'
# nii_template = 'persistentVSremitted_FA_skeletonised.nii.gz'
nii_template = 'nvVSpersistent_FA_skeletonised.nii.gz'
gf = read.csv('~/Documents/philip/dti/FINAL_TSA_allClean149.csv')

# brain_data = read.table('~/data/dti/all_FA_skeleton.txt')
# brain_data = read.table('~/data/dti/persistentVSremitted_FA_skeletonised.txt')
brain_data = read.table('~/data/dti/nvVSpersistent_FA_skeletonised.txt')
out = brain_data[,1:4]

# tmp = gf$SX_inattb
# data = gf$SX_inattb
data = gf$DX_GROUP
nsubj = dim(gf)[1]
tmp = vector()
for (i in 1:nsubj) {
#     if (gf[i,]$DX_GROUP=='persistent') {
    if (gf[i,]$DX_GROUP=='NV') {
        tmp = c(tmp, data[i])
    }
}
for (i in 1:nsubj) {
#     if (gf[i,]$DX_GROUP=='remitted') {
    if (gf[i,]$DX_GROUP=='persistent') {
        tmp = c(tmp, data[i])
    }
}
tmp = as.factor(tmp)
# tmp = -1*tmp

data = as.matrix(brain_data[,4:dim(brain_data)[2]])
nvoxels = dim(data)[1]
stats = vector(length=nvoxels, mode="numeric")
# run the model for the actual data
for (v in 1:nvoxels) {
#     fit = lm(data[v,]~tmp)
    # CHECK THIS FOR EVERY MODEL!
#     stats[v] = summary(fit)$coefficients[2,3]
    stats[v] = t.test(data[v,] ~ tmp, alternative="greater")$statistic
#     stats[v] = cor.test(data[v,], tmp)$statistic
}
# save the statistics to run through TFCE
out[,4] = stats
fname = sprintf('%s/pairwise', out_dir)
# write the t-stats and convert to nifti
write.table(out, file=sprintf('%s.txt',fname), col.names=F, row.names=F)
system(sprintf('cat %s.txt | 3dUndump -master %s/%s -datum float -prefix %s.nii.gz -overwrite -',
               fname, data_dir, nii_template, fname), wait=T)
# run TFCE in the abs(tstats) and convert back to .txt
system(sprintf('fslmaths %s.nii.gz -tfce 2 1 26 %s_tfce.nii.gz', fname, fname), wait=T)
system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s/mean_FA_skeleton_mask.nii.gz %s_tfce.nii.gz',
               fname, data_dir, fname), wait=T)
