# script to grab data from armin_TO in gabrielle and create R files
fname = '~/data/structural/all_data_gf_1473_dsm5_matchedDiff_on18_2to1_v2.RData'
grabCortex = T

mask_ids = read.csv('~/data/structural/gf_1473_dsm45_matched_on18_dsm5_diff_2to1_v2.csv')$maskid
rootFiles = '/Volumes/v3/armin_TO/nih_chp_'

brain_data = c('thalamusL', 'thalamusR', 'striatumL', 'striatumR',
               'gpL', 'gpR')
file_names = c('thalamus_left_vorn_SA_5mm_blur', 'thalamus_right_vorn_SA_5mm_blur',
               'striatum_left_vorn_SA_5mm_blur', 'striatum_right_vorn_SA_5mm_blur',
               'gp_left_vorn_SA_3mm_blur', 'gp_right_vorn_SA_3mm_blur')

for (d in 1:length(brain_data)) {
    cat('\nWorking on', brain_data[d])
    for (i in 1:length(mask_ids)) {
        eval(parse(text=sprintf('subjData = read.table("%s%05g_t1/nih_chp_%05g_t1_%s.txt")',
                                rootFiles, mask_ids[i], mask_ids[i], file_names[d])))
        if (i==1) {
            data = subjData
        }
        else{
            data = cbind(data, subjData)
        }
    }
    eval(parse(text=sprintf('%s = data', brain_data[d])))
}

if (grabCortex) {
    brain_data = c(brain_data, 'cortexL', 'cortexR')
    cat('\nWorking on cortexL')
    for (i in 1:length(mask_ids)) {
        eval(parse(text=sprintf('subjData = read.table("/Volumes/v3/RAID1/CIVET-1.1.10/%05g/surfaces/nih_chp_%05g_mid_surface_rsl_left_native_area_40mm.txt")',
                                 mask_ids[i], mask_ids[i])))
        if (i==1) {
           data = subjData
       }
       else{
           data = cbind(data, subjData)
       }
    }
    cortexL = data
    cat('\nWorking on cortexR')
    for (i in 1:length(mask_ids)) {
        eval(parse(text=sprintf('subjData = read.table("/Volumes/v3/RAID1/CIVET-1.1.10/%05g/surfaces/nih_chp_%05g_mid_surface_rsl_right_native_area_40mm.txt")',
                                mask_ids[i], mask_ids[i])))
        if (i==1) {
            data = subjData
        }
        else{
            data = cbind(data, subjData)
        }
    }
    cortexR = data
}

save(list=brain_data,file=fname)