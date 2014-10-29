# Runs stats on the slopes previously calculated (compute_stats_change.R)
library(nlme)
library(psych)
load('~/research_code/mni_functions.RData')
out_dir='~/data/results/dti_longitudinal/'
data_dir = '~/data/dti_longitudinal/'
prefix = 'matchedByHand'
property = 'FA'
nii_template = sprintf('%s/mean_FA_skeleton_mask.nii.gz',data_dir)
data_name = sprintf('%s/%s_%s_skeletonised.txt', data_dir, prefix, property)
out_name = sprintf('%s/hiCorr_%s_%s', out_dir, prefix, property)


brain_data = read.table(data_name)
out = brain_data[,1:4]

load(sprintf('%s/deltas_%s_%s_.RData', data_dir, prefix, property))

vs = mni.vertex.correlation(changeBrain, changeHI)

# save the actual coefficients (for later visualization)
out[,4] = vs
write.table(out, file=sprintf('%s_coefs.txt',out_name), col.names=F, row.names=F)
system(sprintf('cat %s_coefs.txt | 3dUndump -master %s -datum float -prefix %s_coefs.nii.gz -overwrite -',
               out_name, nii_template, out_name), wait=T)

# convert R to t to become a statistic and run through TFCE
nsubjs = dim(changeBrain)[2]
out[,4] = r2t(vs, nsubjs)

# write the t-stats and convert to nifti
write.table(out, file=sprintf('%s.txt',out_name), col.names=F, row.names=F)
system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -',
               out_name, nii_template, out_name), wait=T)
# run TFCE in the abs(tstats) and convert back to .txt
system(sprintf('fslmaths %s.nii.gz -abs -tfce 2 1 26 %s_tfce.nii.gz', 
               out_name, out_name), wait=T)
system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s %s_tfce.nii.gz',
               out_name, nii_template, out_name), wait=T)

