library(nlme)
load('~/research_code/mni_functions.RData')
out_dir='~/data/results/dti_longitudinal/perms/'
data_dir = '~/data/dti_longitudinal/'
property = 'RD'
prefix = 'matchedByHand'
nii_template = sprintf('%s/mean_FA_skeleton_mask.nii.gz',data_dir)
data_name = sprintf('%s/%s_%s_skeletonised.txt', data_dir, prefix, property)
out_name = sprintf('%s/inattCorr_%s_%s_perm', out_dir, prefix, property)
nperms = 500
set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )


brain_data = read.table(data_name)
out = brain_data[,1:4]

load(sprintf('%s/deltas_%s_%s_.RData', data_dir, prefix, property))
nsubjs = dim(changeBrain)[2]

for (p in 1:nperms) {
    print(sprintf('perm %d',p))
    perm_labels <- sample.int(nsubjs, replace = FALSE)
    rand_data = data[,perm_labels]

    vs = mni.vertex.correlation(rand_data, changeInatt)
    
    out[,4] = r2t(vs, nsubjs)
    
    fname = sprintf('%s_%s-%05f', out_name, Sys.info()["nodename"], runif(1, 1, 99999))
    write.table(out, file=sprintf('%s.txt', fname), col.names=F, row.names=F)
    system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -',
                   fname, nii_template, fname), wait=T)
    system(sprintf('fslmaths %s.nii.gz -abs -tfce 2 1 26 %s_tfce.nii.gz', fname, fname), wait=T)
    system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s %s_tfce.nii.gz',
                   fname, nii_template, fname), wait=T)
    system(sprintf('rm %s.nii.gz %s_tfce.nii.gz', fname, fname), wait=T)
}
