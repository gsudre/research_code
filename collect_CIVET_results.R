# Script to collect all CIVET results onto a set of Freesurfer labels. Need to run freesurfer2civet.py first!
#
# There's some hard code for the longitudinal project, so tread carefully...
# GS, 03/16/2018

# map of integers to freesurfer labels
map_file = '/Volumes/Shaw/longitudinal_anatomy/%s_map_ds.txt'
# map of vertex to freesurfer integers
vertex_file = '/Volumes/Shaw/longitudinal_anatomy/%s_freesurfer2civet_labels_ds.txt'
data_dir = '/Volumes/Shaw/longitudinal_anatomy/CIVET_2.1.0_longitudinal/'

# maskids = c('0119', '0123')
maskids = unlist(lapply(strsplit(list.files(path=data_dir, pattern="*-Mam*", include.dirs=T),
                                 "-"),
                        function(x) x[1]))

data = c()

for (measure in c('area', 'thickness', 'volume')) {
  for (hemi in c('lh', 'rh')) {
    print(sprintf('%s, %s', measure, hemi))
    if (hemi == 'lh') {
      civet_hemi = 'left'
    } else {
      civet_hemi = 'right'
    }
    rois = read.table(sprintf(map_file, hemi))
    vmap = read.table(sprintf(vertex_file, hemi))
    # remove the headers
    vmap = as.numeric(vmap[4:nrow(vmap), 1])
    
    hemi_data = matrix(nrow=length(maskids), ncol=nrow(rois))
    for (m in 1:length(maskids)) {
      # figuring out what file to open
      subj_dir = list.files(path=data_dir, pattern=sprintf("%s-Mam*", maskids[m]),
                            include.dirs=T, full.names=T)
      if (measure == 'thickness') {
        fname = sprintf('%s/thickness/ncr_%s_native_rms_rsl_tlaplace_30mm_%s.txt',
                        subj_dir, maskids[m], civet_hemi)
      } else if (measure == 'area') {
        fname = sprintf('%s/surfaces/ncr_%s_mid_surface_rsl_%s_native_area_40mm.txt',
                        subj_dir, maskids[m], civet_hemi)
      } else {
        fname = sprintf('%s/surfaces/ncr_%s_surface_rsl_%s_native_volume_40mm.txt',
                        subj_dir, maskids[m], civet_hemi)
      }
      
      # reading data and splitting by label
      subj_data = read.table(fname)[, 1]
      for (r in 1:ncol(hemi_data)) {
        hemi_data[m, r] = sum(subj_data[vmap == r])
      }
    }
    
    # formatting header to match Freesurfer standard
    header_template = sprintf('%s_%%s_%s', hemi, measure)
    colnames(hemi_data) = sapply(rois[, 2], function(x) sprintf(header_template, x))
    data = cbind(data, hemi_data)
  }
}