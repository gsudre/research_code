# Runs stats on the slopes previously calculated
library(nlme)
library(psych)
load('~/research_code/mni_functions.RData')
out_dir='~/data/results/dti_longitudinal/'
data_dir = '~/data/dti_longitudinal/'
property = 'FA'
data_name = sprintf('%s/%s_slopes_p2.RData', data_dir, property)
phen_name = sprintf('%s/gf_short_110.csv', data_dir)
out_name = sprintf('%s/ADHD_boys_raw_slopes_%s', out_dir, property)
nii_template = sprintf('%s/mean_FA_skeleton_mask_p2.nii.gz',data_dir)

load(sprintf(data_name))
phen = read.csv(phen_name)

# this should be assigned to either slopes or tvals
brain_data = slopes

# make sure phen and brain_data are in the same order (ascending by MRN)
phen = phen[order(phen$person),]
if (! all(subj_order==phen$person)) {
  print('ERROR!!!! Subjects not in the same order')
}

# select the rows to use
# idx = subj_order>0  # includes everybody
idx = phen$DX=='ADHD' & phen$SEX=='Male' 

data = rowMeans(brain_data[,idx])
out[,4] = data

write.table(out, file=sprintf('%s.txt',out_name), col.names=F, row.names=F)
system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -', out_name, nii_template, out_name), wait=T)

