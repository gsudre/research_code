# Script to collect CIVET parcelation results

# There's some hard code for the longitudinal project, so tread carefully...
# GS, 03/29/2018

data_dir = '/Volumes/Shaw/longitudinal_anatomy/CIVET_2.1.0_cross/'
rois = c('medial_cut_and_brainstem', 'parietal', 'occipital', 'frontal', 'isthmus', 'parahippocampal',
         'cingulate', 'temporal', 'insula', 'total')

# maskids = c('0119', '0123')
maskids = unlist(lapply(strsplit(list.files(path=data_dir, pattern="*-Mam*", include.dirs=T),
                                 "-"),
                        function(x) x[1]))

data = c()

for (measure in c('area', 'thickness', 'volume')) {
  for (hemi in c('left', 'right')) {
    print(sprintf('%s, %s', measure, hemi))
    
    hemi_data = c()
    for (m in 1:length(maskids)) {
      # figuring out what file to open
      subj_dir = list.files(path=data_dir, pattern=sprintf("%s-Mam*", maskids[m]),
                            include.dirs=T, full.names=T)
      if (measure == 'thickness') {
        fname = sprintf('%s/surfaces/ncr_%s_lobes_lobe_thickness_tlaplace_30mm_%s.dat',
                        subj_dir, maskids[m], hemi)
      } else if (measure == 'area') {
        fname = sprintf('%s/surfaces/ncr_%s_lobes_lobe_areas_40mm_%s.dat',
                        subj_dir, maskids[m], hemi)
      } else {
        fname = sprintf('%s/surfaces/ncr_%s_lobes_lobe_volumes_40mm_%s.dat',
                        subj_dir, maskids[m], hemi)
      }
      
      # reading data and splitting by label
      subj_data = read.table(fname)[, 2]
      hemi_data = rbind(hemi_data, subj_data)
    }
    
    # formatting header
    header_template = sprintf('%s_%%s_%s', hemi, measure)
    colnames(hemi_data) = sapply(rois, function(x) sprintf(header_template, x))
    data = cbind(data, hemi_data)
  }
}
data = cbind(maskids, data)
write.csv(data, file='/Volumes/Shaw/longitudinal_anatomy/civet_lobar_labels_cross.csv', quote=F, row.names=F)
