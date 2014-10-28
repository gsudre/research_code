library(nlme)
load('~/research_code/mni_functions.RData')
out_dir='~/data/results/dti_longitudinal/'
data_dir = '~/data/dti_longitudinal/'
prefix = 'matchedByHand'
property = 'TR'
nii_template = sprintf('%s/mean_FA_skeleton_mask.nii.gz',data_dir)
gf_name = sprintf('%s/merged_gf_clinical_neuropsych_clean_matchedByHand.txt', data_dir)
data_name = sprintf('%s/%s_%s_skeletonised.txt', data_dir, prefix, property)
out_name = sprintf('%s/dxAndAge_%s_%s', out_dir, prefix, property)

gf = read.table(gf_name, sep='\t', header=1)
colnames(gf)[3]='age'
colnames(gf)[2]='mrn'
colnames(gf)[5]='dx'

brain_data = read.table(data_name)
out = brain_data[,1:4]

data = as.matrix(brain_data[,4:dim(brain_data)[2]])
# now we need a quick hack to make sure the mni function runs. It always fits the
# first vertex to get the dimensions, but if that breaks the whole function
# breaks. So, let's copy a good voxel to the first position, and then remove it
good_voxel = which(rowSums(data)>0)[1]
data = rbind(data[good_voxel,],data)

vs = mni.vertex.mixed.model(gf, 'y~dx*age', '~1|mrn', data)
interestingTerm = 4

# save the statistics to run through TFCE, taking into account the hack above
out[,4] = vs$t.value[2:dim(data)[1], interestingTerm]

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
out[,4] = vs$value[2:dim(data)[1],interestingTerm]
write.table(out, file=sprintf('%s_coefs.txt',out_name), col.names=F, row.names=F)
system(sprintf('cat %s_coefs.txt | 3dUndump -master %s -datum float -prefix %s_coefs.nii.gz -overwrite -',
               out_name, nii_template, out_name), wait=T)