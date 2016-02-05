# Runs stats on the slopes previously calculated
library(nlme)
library(psych)
load('~/research_code/mni_functions.RData')
out_dir='~/data/results/dti_longitudinal/perms/'
data_dir = '~/data/dti_longitudinal/'
property = 'FA'
adhd_only = FALSE
nperms = 10
target_column = 'HI'
data_name = sprintf('%s/all_%s_skeletonised_p1.txt', data_dir, property)
nii_template = sprintf('%s/mean_FA_skeleton_mask_p1.nii.gz',data_dir)
phen_name = sprintf('%s/DATA_LONG_FROM_256.csv', data_dir)
out_name = sprintf('%s/HI_mixed_%s_perm', out_dir, property)
fixed_effect = sprintf('y ~ %s',target_column)
random_effect = sprintf('~1|ID')

set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )

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

nsubjs = dim(phen)[1]

for (p in 1:nperms) {
    print(sprintf('perm %d',p))
    perm_labels <- sample.int(nsubjs, replace = FALSE)
    rand_data = brain_data[,perm_labels]

    # the meat of the script
    vs = mni.vertex.mixed.model(phen, fixed_effect, random_effect, rand_data)

    # statistics and run through TFCE
    out[,4] = vs$t.value[,2]

    fname = sprintf('%s_%s-%05f', out_name, Sys.info()["nodename"], runif(1, 1, 99999))
    write.table(out, file=sprintf('%s.txt', fname), col.names=F, row.names=F)
    system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -',
                   fname, nii_template, fname), wait=T)
    system(sprintf('fslmaths %s.nii.gz -abs -tfce 2 1 26 %s_tfce.nii.gz', fname, fname), wait=T)
    system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s %s_tfce.nii.gz',
                   fname, nii_template, fname), wait=T)
    system(sprintf('rm %s.nii.gz %s_tfce.nii.gz', fname, fname), wait=T)
}
