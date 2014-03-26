out_dir='~/data/results/tfce/'
data_dir = '~/data/dti/'
nii_template = 'all_FA_skeletonised.nii.gz'
gf = read.csv('~/Documents/philip/dti/FINAL_TSA_allClean149.csv')
tmp = gf$SX_inattb
brain_data = read.table('~/data/dti/all_FA_skeleton.txt')
out = brain_data[,1:4]
data = as.matrix(brain_data[,4:dim(brain_data)[2]])
nvoxels = dim(data)[1]
stats = vector(length=nvoxels, mode="numeric")
for (v in 1:dim(data)[1]) {
    fit = lm(data[v,]~tmp)
    # CHECK THIS FOR EVERY MODEL!
    stats[v] = summary(fit)$coefficients[2,3]
}
out[,4] = stats
fname = sprintf('%s/inatt_with_NVs', out_dir)
write.table(out, file=sprintf('%s.txt',fname), col.names=F, row.names=F)
system(sprintf('cat %s.txt | 3dUndump -master %s/%s -datum float -prefix %s.nii.gz -overwrite -',
               fname, data_dir, nii_template, fname), wait=T)
system(sprintf('fslmaths %s.nii.gz -tfce 2 1 26 %s_tfce.nii.gz', fname, fname), wait=T)
system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s/mean_FA_skeleton_mask.nii.gz %s_tfce.nii.gz',
               fname, data_dir, fname), wait=T)