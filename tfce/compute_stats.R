load('~/research_code/mni_functions.RData')
out_dir='~/data/results/dti_longitudinal/'
data_dir = '~/data/dti_longitudinal/'
nii_template = sprintf('%s/mean_FA_skeleton_mask.nii.gz',data_dir)
gf_name = sprintf('%s/nv_boys_gf.txt', data_dir)
data_name = sprintf('%s/all_FA_skeletonised.txt', data_dir)
out_name = sprintf('%s/linear_growth', out_dir)

gf = read.table(gf_name, sep='\t', header=1)
colnames(gf) = c('maskid','mrn','age')
brain_data = read.table(data_name)
out = brain_data[,1:4]

data = as.matrix(brain_data[,4:dim(brain_data)[2]])
vs = mni.vertex.mixed.model(gf, 'y~age', '~1|mrn', data)

# save the statistics to run through TFCE
out[,4] = vs$t.value[,2]

# write the t-stats and convert to nifti
write.table(out, file=sprintf('%s.txt',out_name), col.names=F, row.names=F)
system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -',
               out_name, nii_template, out_name), wait=T)
# run TFCE in the abs(tstats) and convert back to .txt
system(sprintf('fslmaths %s.nii.gz -abs -tfce 2 1 26 %s_tfce.nii.gz', 
               out_name, out_name), wait=T)
system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s %s_tfce.nii.gz',
               out_name, nii_template, out_name), wait=T)
