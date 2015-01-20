# Runs stats on the slopes previously calculated
library(nlme)
library(psych)
load('~/research_code/mni_functions.RData')
out_dir='~/data/results/dti_longitudinal/'
data_dir = '~/data/dti_longitudinal/'
property = 'FA'
adhd_only = FALSE
target_column = 'HI_SLOPE'
data_name = sprintf('%s/%s_slopes_p2.RData', data_dir, property)
phen_name = sprintf('%s/gf_short_110.csv', data_dir)
out_name = sprintf('%s/HI_slopes_%s', out_dir, property)
test_formula = sprintf('y ~ %s',target_column)
nii_template = sprintf('%s/mean_FA_skeleton_mask_p2.nii.gz',data_dir)

load(sprintf(data_name))
phen = read.csv(phen_name)
brain_data = slopes

# make sure phen and brain_data are in the same order (ascending by MRN)
phen = phen[order(phen$person),]
if (! all(subj_order==phen$person)) {
  print('ERROR!!!! Subjects not in the same order')
}

# select the rows to use
idx = subj_order>0  # includes everybody
# idx = phen$DX=='ADHD' & phen$SEX=='Male' 

phen = phen[idx,]
brain_data = brain_data[,idx]
subj_order = subj_order[idx]

# the meat of the script
vs = mni.vertex.statistics(phen, test_formula, brain_data)

# save the actual coefficients (for later visualization)
out[,4] = vs$slope[,2]
write.table(out, file=sprintf('%s_coefs.txt',out_name), col.names=F, row.names=F)
system(sprintf('cat %s_coefs.txt | 3dUndump -master %s -datum float -prefix %s_coefs.nii.gz -overwrite -',
               out_name, nii_template, out_name), wait=T)


# statistics and run through TFCE
out[,4] = vs$tstatistic[,2]

# write the t-stats and convert to nifti
write.table(out, file=sprintf('%s.txt',out_name), col.names=F, row.names=F)
system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -',
               out_name, nii_template, out_name), wait=T)
# run TFCE in the abs(tstats) and convert back to .txt
system(sprintf('fslmaths %s.nii.gz -abs -tfce 2 1 26 %s_tfce.nii.gz', 
               out_name, out_name), wait=T)
system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s %s_tfce.nii.gz',
               out_name, nii_template, out_name), wait=T)
