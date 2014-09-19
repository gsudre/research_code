mode = 'tfce' # 'vox' or 'tfce'
nvoxels = 73360
res_name = 'linear_growth_FA'
nii_template = '~/data/dti_longitudinal/mean_FA_skeleton_mask.nii.gz'
perm_dir='~/data/results/dti_longitudinal/perms/'
res_dir='~/data/results/dti_longitudinal/'

if (mode=='tfce') {
    fname = sprintf('%s/%s_tfce.txt', res_dir, res_name)
    pattern = 'tfce.txt$' # ends in tfce
} else {
    fname = sprintf('%s/%s.txt', res_dir, res_name)
    pattern = '[0-9].txt$' # ends in a number
}
files = list.files(perm_dir, pattern=pattern)
nperms = length(files)
null_dist_corr = vector(length=nperms) 
ps = vector(length=nvoxels, mode='integer')
results = read.table(fname)
out = results[,1:4]
results = as.matrix(results[,4:dim(results)[2]])
for (f in 1:nperms) {
    cat(f, '/', nperms, '\n')
    data = read.table(sprintf("%s/%s", perm_dir, files[f]))
    data = as.matrix(data[,4:dim(data)[2]])
    null_dist_corr[f] = max(data)
    idx = data > results 
    ps[idx] = ps[idx] + 1
}
ps = ps/nperms
out[,4] = 1-ps
fname = sprintf('%s/%s_%s_p', res_dir, res_name, mode)
write.table(out, file=sprintf('%s.txt', fname), col.names=F, row.names=F)
system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -',
               fname, nii_template, fname), wait=T)

corrps = ps  # just initializing it
for (v in 1:nvoxels) {
    corrps[v] = sum(null_dist_corr > results[v])/nperms
}
out[,4] = 1-corrps
fname = sprintf('%s/%s_%s_corrp', res_dir, res_name, mode)
write.table(out, file=sprintf('%s.txt', fname), col.names=F, row.names=F)
system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -',
               fname, nii_template, fname), wait=T)