library(nlme)
load('~/research_code/mni_functions.RData')
out_dir='~/tmp/perms/'
data_dir = '/mnt/neuro/dti_longitudinal/analysis_robust_upTo1502/tbss/stats/'
property = 'FA'
prefix = 'matchedByHand'
nii_template = sprintf('%s/mean_FA_skeleton_mask.nii.gz',data_dir)
data_name = sprintf('%s/all_FA_skeletonised.txt', data_dir)
out_name = sprintf('%s/tmp_perm', out_dir)
nperms = 5000
set.seed( as.integer((as.double(Sys.time())*1000+Sys.getpid()) %% 2^31) )

v0 = vector(length=130)
v1 = vector(length=164)
v0[]=0
v1[]=1
v = as.factor(c(v0,v1))

brain_data = read.table(data_name)
out = brain_data[,1:4]

data = as.matrix(brain_data[,4:dim(brain_data)[2]])
# now we need a quick hack to make sure the mni function runs. It always fits the
# first vertex to get the dimensions, but it that break,s the whole function
# breaks. So, let's copy a good voxel to the first position, and then remove it
good_voxel = which(rowSums(data)>0)[1]
data = rbind(data[good_voxel,],data)
gf = data.frame(dx=v)

interestingTerm = 2

for (p in 1:nperms) {
    print(sprintf('perm %d',p))
    perm_labels <- sample.int(dim(data)[2], replace = FALSE)
    rand_data = data[,perm_labels]

    # vs = mni.vertex.mixed.model(gf, 'y~inatt*age', '~1|mrn', rand_data)
    vs = mni.vertex.statistics(gf, 'y~dx', rand_data)
    
    # save the statistics to run through TFCE, taking into account the hack above
    # out[,4] = vs$t.value[2:dim(data)[1],interestingTerm]
    out[,4] = vs$tstatistic[2:dim(data)[1], interestingTerm]

    fname = sprintf('%s_%s-%05f', out_name, Sys.info()["nodename"], runif(1, 1, 99999))
    write.table(out, file=sprintf('%s.txt', fname), col.names=F, row.names=F)
    system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -',
                   fname, nii_template, fname), wait=T)
    system(sprintf('fslmaths %s.nii.gz -abs -tfce 2 1 26 %s_tfce.nii.gz', fname, fname), wait=T)
    system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s %s_tfce.nii.gz',
                   fname, nii_template, fname), wait=T)
    system(sprintf('rm %s.nii.gz %s_tfce.nii.gz', fname, fname), wait=T)
}
