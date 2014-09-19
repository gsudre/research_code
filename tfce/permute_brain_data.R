load('~/research_code/mni_functions.RData')
out_dir='~/data/results/dti_longitudinal/perms/'
data_dir = '~/data/dti_longitudinal/'
nii_template = sprintf('%s/mean_FA_skeleton_mask.nii.gz',data_dir)
gf_name = sprintf('%s/nv_boys_gf.txt', data_dir)
property = 'FA'
data_name = sprintf('%s/all_%s_skeletonised.txt', data_dir, property)
out_name = sprintf('%s/linear_growth_%s_perm', out_dir, property)
nperms = 3
set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )

gf = read.table(gf_name, sep='\t', header=1)
colnames(gf) = c('maskid','mrn','age')
brain_data = read.table(data_name)
out = brain_data[,1:4]

data = as.matrix(brain_data[,4:dim(brain_data)[2]])
# now we need a quick hack to make sure the mni function runs. It always fits the
# first vertex to get the dimensions, but it that break,s the whole function
# breaks. So, let's copy a good voxel to the first position, and then remove it
good_voxel = which(rowSums(data)>0)[1]
data = rbind(data[good_voxel,],data)

for (p in 1:nperms) {
    print(sprintf('perm %d',p))
    perm_labels <- sample.int(dim(data)[2], replace = FALSE)
    rand_data = data[,perm_labels]
    vs = mni.vertex.mixed.model(gf, 'y~age', '~1|mrn', rand_data)
    # save the statistics to run through TFCE, taking into account the hack above
    out[,4] = vs$t.value[2:dim(data)[1],2]
    
    fname = sprintf('%s_%s-%05f', out_name, Sys.info()["nodename"], runif(1, 1, 99999))
    write.table(out, file=sprintf('%s.txt', fname), col.names=F, row.names=F)
    system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -',
                   fname, nii_template, fname), wait=T)
    system(sprintf('fslmaths %s.nii.gz -tfce 2 1 26 %s_tfce.nii.gz', fname, fname), wait=T)
    system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s/mean_FA_skeleton_mask.nii.gz %s_tfce.nii.gz',
                   fname, data_dir, fname), wait=T)
    system(sprintf('rm %s.nii.gz %s_tfce.nii.gz', fname, fname), wait=T)
}
