# script to grab volumetric data from gabrielle and create R files
fname = '~/data/structural/cortical_volumes_gf_1473_dsm5_matchedDiff_on18_2to1_v2.RData'

mask_ids = read.csv('~/data/structural/gf_1473_dsm45_matched_on18_dsm5_diff_2to1_v2.csv')$maskid
rootFiles = '/Volumes/v3/RAID1/CIVET-1.1.10/%05g/segment/nih_chp_%05g_fine_structures.dat'

rois = read.csv('~/data/structural/useful_cortical_volume_labels.csv')
cortexVol = matrix(nrow=length(mask_ids), ncol=dim(rois)[1],
                   dimnames=list(mask_ids,rois$label))

for (d in 1:dim(rois)[1]) {
    cat('\nWorking on', rois[d,]$label)
    for (i in 1:length(mask_ids)) {
        eval(parse(text=sprintf('subjData = read.table("%s")',
                                sprintf(rootFiles, mask_ids[i], mask_ids[i]))))
        roiIdx = which(subjData[,1]==rois[d,]$num)
        cortexVol[i,d] = subjData[roiIdx,2]
    }
}

save(cortexVol,file=fname)

# this is not in gabrielle, but we need it for the analysis too
a = read.csv('~/data/structural/VOLUMES_SA_SOOURCE_OCT_2012.csv')
subcorticalVol = array(dim=c(length(maskid),28))
colnames(subcorticalVol) = colnames(a)[c(2:7,14:35)]
for (i in 1:length(maskid)) {
    idx = which(a[,1]==maskid[i])
    subcorticalVol[i,] = as.numeric(a[idx,c(2:7,14:35)])
}
save(subcorticalVol,file='~/data/structural/subcortical_volumes_gf_1473_dsm5_matchedDiff_on18_2to1_v2.RData')