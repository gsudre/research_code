# Runs stats on the slopes previously calculated
library(nlme)
library(psych)
load('~/research_code/mni_functions.RData')
out_dir='~/data/results/dti_longitudinal/'
data_dir = '~/data/dti_longitudinal/'
property = 'FA'
adhd_only = FALSE
target_column = 'HI'
data_name = sprintf('%s/all_%s_skeletonised_p2.txt', data_dir, property)
nii_template = sprintf('%s/mean_FA_skeleton_mask_p2.nii.gz',data_dir)
phen_name = sprintf('%s/DATA_LONG_FROM_256.csv', data_dir)
out_name = sprintf('%s/HI_mixed_%s', out_dir, property)
fixed_effect = sprintf('y ~ %s',target_column)
random_effect = sprintf('~1|ID')


brain_data = read.table(data_name)
phen = read.csv(phen_name)

# grabbing voxel i,j,k
out = brain_data[,1:4]
brain_data = as.matrix(brain_data[,4:dim(brain_data)[2]])

# organize phen table to match brain data (organized by maskid order)
phen = phen[order(phen$MASKID),]

# remove any data where the target phen column is NA
eval(parse(text=sprintf('column_data = phen$\"%s\"', target_column)))
idx = !is.na(column_data)
brain_data = brain_data[,idx]
phen = phen[idx,]

# exclude NVs if so desired
if (adhd_only==TRUE) {
    idx = phen$DX=='ADHD'
    brain_data = brain_data[,idx]
    phen = phen[idx,]
}

# the meat of the script
vs = mni.vertex.mixed.model(phen, fixed_effect, random_effect, brain_data)

# save the actual coefficients (for later visualization)
out[,4] = vs$value[,2]
write.table(out, file=sprintf('%s_coefs.txt',out_name), col.names=F, row.names=F)
system(sprintf('cat %s_coefs.txt | 3dUndump -master %s -datum float -prefix %s_coefs.nii.gz -overwrite -',
               out_name, nii_template, out_name), wait=T)


# statistics and run through TFCE
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
