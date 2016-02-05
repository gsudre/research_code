# compute stats on permuted data
library(nlme)
library(psych)
load('~/research_code/mni_functions.RData')
out_dir='~/data/results/dti_longitudinal/perms'
data_dir = '~/data/dti_longitudinal/'
property = 'FA'
adhd_only = FALSE
target_column = 'HI_SLOPE'
data_name = sprintf('%s/%s_slopes_p2.RData', data_dir, property)
phen_name = sprintf('%s/gf_short_110.csv', data_dir)
out_name = sprintf('%s/HI_slopes_%s_perm', out_dir, property)
test_formula = sprintf('y ~ %s',target_column)
nperms = 10
nii_template = sprintf('%s/mean_FA_skeleton_mask_p2.nii.gz',data_dir)

# setting random seed and loading data and phenotype files
set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )

load(sprintf(data_name))
phen = read.csv(phen_name)

# identify what brain data we're using
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

nsubjs = length(subj_order)

for (p in 1:nperms) {
    print(sprintf('perm %d',p))
    perm_labels <- sample.int(nsubjs, replace = FALSE)
    rand_data = brain_data[,perm_labels]

    vs = mni.vertex.statistics(phen, test_formula, rand_data)
    out[,4] = vs$tstatistic[,2]
    
    fname = sprintf('%s_%s-%05f', out_name, Sys.info()["nodename"], runif(1, 1, 99999))
    write.table(out, file=sprintf('%s.txt', fname), col.names=F, row.names=F)
    system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -',
                   fname, nii_template, fname), wait=T)
    system(sprintf('fslmaths %s.nii.gz -abs -tfce 2 1 26 %s_tfce.nii.gz', fname, fname), wait=T)
    system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s %s_tfce.nii.gz',
                   fname, nii_template, fname), wait=T)
    system(sprintf('rm %s.nii.gz %s_tfce.nii.gz', fname, fname), wait=T)
}
