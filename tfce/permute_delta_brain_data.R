library(nlme)
library(psych)
load('~/research_code/mni_functions.RData')
out_dir='~/data/results/dti_longitudinal/perms/'
data_dir = '~/data/dti_longitudinal/'
property = 'FA'
prefix = 'all'
nii_template = sprintf('%s/mean_FA_skeleton_mask.nii.gz',data_dir)
data_name = sprintf('%s/%s_%s_skeletonised.txt', data_dir, prefix, property)
out_name = sprintf('%s/hiCorr_%s_%s_perm', out_dir, prefix, property)
nperms = 100
set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )


brain_data = read.table(data_name)
out = brain_data[,1:4]

load(sprintf('%s/deltasWithNVs_%s_%s.RData', data_dir, prefix, property))

idx = dx==1 # ADHD=1, NV=2
changeBrain = changeBrain[,idx]
changeInatt = changeInatt[idx]
changeHI = changeHI[idx]

nsubjs = dim(changeBrain)[2]

for (p in 1:nperms) {
    print(sprintf('perm %d',p))
    perm_labels <- sample.int(nsubjs, replace = FALSE)
    rand_data = changeBrain[,perm_labels]

    # tmp = data.frame(dx=as.factor(dx))
    # vs = mni.vertex.statistics(tmp, 'y~dx', rand_data)
    # out[,4] = vs$tstatistic[,2]

    vs = mni.vertex.correlation(rand_data, changeHI)
    out[,4] = r2t(vs, nsubjs)
    
    fname = sprintf('%s_%s-%05f', out_name, Sys.info()["nodename"], runif(1, 1, 99999))
    write.table(out, file=sprintf('%s.txt', fname), col.names=F, row.names=F)
    system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -',
                   fname, nii_template, fname), wait=T)
    system(sprintf('fslmaths %s.nii.gz -abs -tfce 2 1 26 %s_tfce.nii.gz', fname, fname), wait=T)
    system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s %s_tfce.nii.gz',
                   fname, nii_template, fname), wait=T)
    system(sprintf('rm %s.nii.gz %s_tfce.nii.gz', fname, fname), wait=T)
}
