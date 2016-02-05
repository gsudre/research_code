# Merges voxels across tracts (columns) for all mask ids (rows). Later still need to concatenate the rows if needed to combine longitudinal and cross secitonal data
prop = 'rd'
nsubj = 174
# SOMETHING WEIRD WITH SPLENIUM... DIFFERENT NUMBER OF VOXELS BETWEEN CS AND LONGITUDINAL. NEED TO ADD IT LATER AND CHECK WHAT'S GOING ON
tracts = c('Arc_R_resampled','Arc_L_resampled','UNC_R_resampled',
           'UNC_L_resampled','ILF_IFOF_R_resampled',
           'ILF_IFOF_L_resampled','PostIntCaps_Cereb_R_resampled',
           'PostIntCaps_Cereb_L_resampled','CF-R-M_resampled',
           'CF-L-M_resampled','Fornix_resampled','CC_Genu_resampled',
           'CC_Tapetum_resampled')
all_data = matrix(nrow=1,ncol=nsubj)
row_names = vector()
cnt=1
for (t in tracts) {
    fname = sprintf('~/data/dti_longitudinal/tracts/output_cs/FiberProfiles/%s/%s_%s.csv',t,prop,t)
    data = read.csv(fname)
    idx = 2:(nsubj+1)
    all_data = rbind(all_data, as.matrix(data[,idx]))
    for (i in 1:dim(data)[1]) {row_names = c(row_names, sprintf('%s_%d',t,i))}
}
# remove extra row
all_data = all_data[2:dim(all_data)[1],]
colnames(all_data) = colnames(data)[idx]
rownames(all_data) = row_names
save(all_data,file=sprintf('~/tmp/%s_%d.RData',prop,nsubj))



