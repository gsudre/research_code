library(nlme)
load('~/research_code/mni_functions.RData')
out_dir='~/data/results/dti_longitudinal/'
data_dir = '~/data/dti_longitudinal/'
nii_template = sprintf('%s/mean_FA_skeleton_mask.nii.gz',data_dir)
gf_name = sprintf('%s/nv_boys_gf.txt', data_dir)
property = 'FA'
data_name = sprintf('%s/all_%s_skeletonised.txt', data_dir, property)
out_name = sprintf('%s/linear_growth_%s', out_dir, property)

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
vs = mni.vertex.mixed.model(gf, 'y~age', '~1|mrn', data)

# save the statistics to run through TFCE, taking into account the hack above
out[,4] = vs$t.value[2:dim(data)[1],2]

# write the t-stats and convert to nifti
write.table(out, file=sprintf('%s.txt',out_name), col.names=F, row.names=F)
system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -',
               out_name, nii_template, out_name), wait=T)
# run TFCE in the abs(tstats) and convert back to .txt
system(sprintf('fslmaths %s.nii.gz -abs -tfce 2 1 26 %s_tfce.nii.gz', 
               out_name, out_name), wait=T)
system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s %s_tfce.nii.gz',
               out_name, nii_template, out_name), wait=T)

# save the actual coefficients (for later visualization)
out[,4] = vs$value[2:dim(data)[1],2]
write.table(out, file=sprintf('%s_coefs.txt',out_name), col.names=F, row.names=F)
system(sprintf('cat %s_coefs.txt | 3dUndump -master %s -datum float -prefix %s_coefs.nii.gz -overwrite -',
               out_name, nii_template, out_name), wait=T)