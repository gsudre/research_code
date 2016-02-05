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

vs = mni.vertex.statistics(gf, 'y~dx', data)

# save the statistics to run through TFCE, taking into account the hack above
# out[,4] = vs$t.value[2:dim(data)[1], interestingTerm]
out[,4] = vs$tstatistic[2:dim(data)[1], interestingTerm]

# write the t-stats and convert to nifti
write.table(out, file=sprintf('%s.txt',out_name), col.names=F, row.names=F)
system(sprintf('cat %s.txt | 3dUndump -master %s -datum float -prefix %s.nii.gz -overwrite -',
               out_name, nii_template, out_name), wait=T)
# run TFCE in the abs(tstats) and convert back to .txt
system(sprintf('fslmaths %s.nii.gz -abs -tfce 2 1 26 %s_tfce.nii.gz', 
               out_name, out_name), wait=T)
system(sprintf('3dmaskdump -o %s_tfce.txt -overwrite -mask %s %s_tfce.nii.gz',
               out_name, nii_template, out_name), wait=T)

# save the actual coefficients (for later visualization)
# out[,4] = vs$value[2:dim(data)[1],interestingTerm]
out[,4] = vs$slope[2:dim(data)[1],interestingTerm]
write.table(out, file=sprintf('%s_coefs.txt',out_name), col.names=F, row.names=F)
system(sprintf('cat %s_coefs.txt | 3dUndump -master %s -datum float -prefix %s_coefs.nii.gz -overwrite -',
               out_name, nii_template, out_name), wait=T)