# Script to collect all CIVET results onto a set of Freesurfer labels. Need to run freesurfer2civet.py first!
#
# There's some hard code for the longitudinal project, so tread carefully...
# GS, 03/16/2018

# map of integers to freesurfer labels
map_file = '/Volumes/Shaw/longitudinal_anatomy/%s_map_ds.txt'
# map of vertex to freesurfer integers
vertex_file = '/Volumes/Shaw/longitudinal_anatomy/%s_freesurfer2civet_labels_ds.txt'
data_dir = '/Volumes/Shaw/longitudinal_anatomy/CIVET_2.1.0_cross/'

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
    # remove the headers
    vmap = read.table(sprintf(vertex_file, hemi), skip=3)
    
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
data = cbind(maskids, data)
save(data, file='/Volumes/Shaw/longitudinal_anatomy/civet_in_freesurfer_labels_cross.RData')



# a = read.csv('/Volumes/Shaw/longitudinal_anatomy/demo_long.csv')
# b = read.csv('/Volumes/Shaw/longitudinal_anatomy/mriqc_longitudinal/T1w.csv')
# colnames(b) = sapply(colnames(b), function(x) { sprintf('mriqc_%s', x) } )
# m = merge(a, b, by.x='Mask.ID...Scan', by.y='mriqc_session_id', all.x=T)
# b = read.table('/Volumes/Shaw/longitudinal_anatomy/freesurfer_output_longitudinal/cross_pipeline/merged_rois.txt', header=1)
# colnames(b) = sapply(colnames(b), function(x) { sprintf('freesurfer_crossPipe_%s', x) } )
# m = merge(m, b, by.x='Mask.ID...Scan', by.y='freesurfer_crossPipe_lh.aparc.area', all.x=T)
# b = read.csv('/Volumes/Shaw/longitudinal_anatomy/freesurfer_qc.csv')
# colnames(b) = sapply(colnames(b), function(x) { sprintf('freesurferQC_%s', x) } )
# m = merge(m, b, by.x='Mask.ID...Scan', by.y='freesurferQC_Mask.ID...QualityControl', all.x=T)
# b = read.table('/Volumes/Shaw/longitudinal_anatomy/freesurfer_output_longitudinal/longitudinal_pipeline/merged_rois.txt', header=1)
# colnames(b) = sapply(colnames(b), function(x) { sprintf('freesurfer_longPipe_%s', x) } )
# m = merge(m, b, by.x='Mask.ID...Scan', by.y='freesurfer_longPipe_lh.aparc.area', all.x=T)
# b = read.csv('/Volumes/Shaw/longitudinal_anatomy/CIVET_2.1.0_longitudinal/Study-1521129234/QC/civet_ncr_.csv')
# colnames(b) = sapply(colnames(b), function(x) { sprintf('CIVET_%s', x) } )
# m = merge(m, b, by.x='Mask.ID...Scan', by.y='CIVET_ID', all.x=T)


# source('~/research_code/lab_mgmt/merge_on_closest_date.R')
# my_ids = unique(a$Medical.Record...MRN...Subjects)
# df3 = mergeOnClosestDate(a, b, my_ids, x.id='Medical.Record...MRN...Subjects', y.id='Medical.Record...MRN...Subjects', y.date='Date.tested...WASI.I...WASI.II...WPPSI.III...WPPSI.IV...WTAR...Subjects', x.date='record.date.collected...Scan')
# colnames(df3)[16] = 'dateScan.minus.dateIQ.months'
# d = read.csv('/Volumes/Shaw/longitudinal_anatomy/clinical_03202018.csv')
# m = mergeOnClosestDate(df3, d, my_ids, x.id='Medical.Record...MRN...Subjects', y.id='MRN', y.date='Date', x.date='record.date.collected...Scan')
# colnames(m)[25] = 'dateScan.minus.dateClinical.months'
# write.csv(m, row.names=F, file='/Volumes/Shaw/longitudinal_anatomy/gf_cross_03202018.csv')

