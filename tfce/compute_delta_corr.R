# Runs stats on the slopes previously calculated
library(nlme)
library(psych)
load('~/research_code/mni_functions.RData')
out_dir='~/data/results/dti_longitudinal/'
data_dir = '~/data/dti_longitudinal/'
property = 'RD'
adhd_only = TRUE
target_column = 'HI_109'
data_name = sprintf('%s/slopes_upTo1502_11242014.RData', data_dir)
phen_name = sprintf('%s/phen_short_form.csv', data_dir)
out_name = sprintf('%s/mytestname_%s', out_dir, property)
test_formula = sprintf('y ~ %s',target_column)
nii_template = sprintf('%s/mean_FA_skeleton_mask.nii.gz',data_dir)


load(sprintf(data_name))
phen = read.csv(phen_name)

# identify what brain data we're using
eval(parse(text=sprintf('brain_data = %s_slopes', property)))

# organize subjects in data matrix in the same order as phen table. Just re-sort both of them based on MRN
brain_data = brain_data[,order(subj_order)]
subj_order = subj_order[order(subj_order)]
phen = phen[order(phen$person),]

# remove any data where the target phen column is NA
eval(parse(text=sprintf('column_data = phen$\"%s\"', target_column)))
idx = !is.na(column_data)
brain_data = brain_data[,idx]
subj_order = subj_order[idx]
phen = phen[idx,]

# exclude NVs if so desired
if (adhd_only==TRUE) {
    idx = phen$DX=='ADHD'
    brain_data = brain_data[,idx]
    phen = phen[idx,]
}

# vs = mni.vertex.correlation(changeBrain, changeHI)

vs = mni.vertex.statistics(phen, test_formula, brain_data)

# save the actual coefficients (for later visualization)
# out[,4] = vs
out[,4] = vs$slope[,2]
write.table(out, file=sprintf('%s_coefs.txt',out_name), col.names=F, row.names=F)
system(sprintf('cat %s_coefs.txt | 3dUndump -master %s -datum float -prefix %s_coefs.nii.gz -overwrite -',
               out_name, nii_template, out_name), wait=T)

# # convert R to t to become a statistic and run through TFCE
# nsubjs = dim(changeBrain)[2]
# out[,4] = r2t(vs, nsubjs)

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

