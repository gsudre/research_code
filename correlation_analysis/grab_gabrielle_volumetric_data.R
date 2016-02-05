# script to grab volumetric data from gabrielle and create R files
fname = '~/data/structural/normalization_volumes_gf1473.RData'

load('~/data/structural/just_gf1473_dsm45.RData')
mask_ids = gf_1473$MASKID.x
lobesFiles = '/Volumes/v2/CIVET-1.1.10/CIVET%01g/%05g/segment/nih_chp_%05g_lobes.dat'
icvFiles = '/Volumes/v2/CIVET-1.1.10/CIVET%01g/%05g/classify/nih_chp_%05g_cls_volumes.dat'

rois = read.csv('~/data/structural/useful_cortical_volume_labels.csv')
normVol = matrix(nrow=length(mask_ids), ncol=6)
colnames(normVol) = c('maskid','icv','Lwm','Rwm','Lgm','Rgm')

for (i in 1:length(mask_ids)) {
    cat('\nWorking on', i, length(mask_ids))
    eval(parse(text=sprintf('subjData = read.table("%s")',
                            sprintf(icvFiles, floor(mask_ids[i]/1000), mask_ids[i], mask_ids[i]))))
    normVol[i,1] = mask_ids[i]
    normVol[i,2] = sum(subjData[,2])
    eval(parse(text=sprintf('subjData = read.table("%s")',
                            sprintf(lobesFiles, floor(mask_ids[i]/1000), mask_ids[i], mask_ids[i]))))
    normVol[i,6] = sum(subjData[c(1,4,28,26,24,22,20),2])
    normVol[i,5] = sum(subjData[c(5,6,7,8,19,21,23,25,27),2])
    normVol[i,4] = sum(subjData[c(9,11,13,15,17),2])
    normVol[i,3] = sum(subjData[c(10,12,18),2])
}

source('~/research_code/correlation_analysis/macacc_massage_data_matched_diff.R')
source('~/research_code/correlation_analysis/compile_baseline.R')
nsubjs = dim(gfBase)[1]
normVolumeBase = matrix(nrow=nsubjs, ncol=6)
colnames(normVolumeBase) = c('maskid','icv','Lwm','Rwm','Lgm','Rgm')
for (i in 1:nsubjs) {
    cat('\nWorking on', i, nsubjs)
    maskid = gfBase[i,]$MASKID.x
    eval(parse(text=sprintf('subjData = read.table("%s")',
                            sprintf(icvFiles, floor(maskid/1000), maskid, maskid))))
    normVolumeBase[i,1] = maskid
    normVolumeBase[i,2] = sum(subjData[,2])
    eval(parse(text=sprintf('subjData = read.table("%s")',
                            sprintf(lobesFiles, floor(maskid/1000), maskid, maskid))))
    normVolumeBase[i,6] = sum(subjData[c(1,4,28,26,24,22,20),2])
    normVolumeBase[i,5] = sum(subjData[c(5,6,7,8,19,21,23,25,27),2])
    normVolumeBase[i,4] = sum(subjData[c(9,11,13,15,17),2])
    normVolumeBase[i,3] = sum(subjData[c(10,12,18),2])
}
save(normVol,normVolumeBase,file=fname)