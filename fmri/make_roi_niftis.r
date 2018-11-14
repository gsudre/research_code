# Goal is to make Nifti files (one per subject) that contains just the ROI data,
# so we can run it through ICA.
# We also output the concatenated data over time for possible use in ICASSO.
#
# GS, 11/2018


input_dir = '~/data/baseline_prediction/rsfmri/'
output_dir = '~/data/baseline_prediction/rsfmri/roi_niftis/'
trimmed = F  # whether to trim subjects with good TR > 123
p = 'aparc'

# some non-grey mater ROIs we don't need
rm_rois = c('CSF', 'Ventricle$', 'Pallidum$', 'Brain.Stem',
            'Accumbens.area$', 'VentralDC$', 'vessel$', 'Cerebral',
            'choroid', 'Lat.Vent$', 'White.Matter$', 'hypointensities',
            '^CC', 'nknown$', 'Chiasm$', 'Cerebellum.Cortex$')

# get labels but ignoring junk in beginnig and end of file
roi_fname = sprintf('%s/%s+aseg_REN_all.niml.lt', input_dir, p)
flen = length(readLines(roi_fname))
roi_table = read.table(roi_fname, skip=4, nrows=(flen-7))

rm_me = c()
for (r in rm_rois) {
    rm_me = c(rm_me, which(grepl(r, roi_table[, 2])))
}
roi_table = roi_table[-rm_me, ]

all_scans = c()
library(oro.nifti)
# get list of subjects from directory
maskids = list.files(path=sprintf('%s/%s/', input_dir, p), pattern='*')
for (m in maskids) {
    print(m)
    scan_dir = sprintf('%s/%s/%s/', input_dir, p, m)
    oneds = list.files(path=scan_dir, pattern='*.1D')
    ntrs = sapply(oneds, function(x) length(readLines(sprintf('%s/%s',
                                                            scan_dir, x))))
    # only grabing data for ROIs that we want to include
    scan_data = matrix(data=0, nrow=max(ntrs), ncol=nrow(roi_table))
    colnames(scan_data) = roi_table[, 2]
    for (roi in roi_table[, 2]) {
        roi_num = roi_table[roi_table[, 2] == roi, 1]
        # read in data for nonempty ROIs. Empty ROIs stay as NAs
        fname_1d = sprintf('%d.1D', roi_num)
        if (ntrs[fname_1d] > 0) {
            scan_data[, roi] = as.numeric(readLines(sprintf('%s/%s',
                                                            scan_dir,
                                                            fname_1d)))
        }
    }
    # remove any TRs that are all zeros (censored TRs)
    nonempty_rois = sum(!is.na(scan_data[1, ]))
    good_trs = rowSums(scan_data==0, na.rm=T) != nonempty_rois
    scan_data = scan_data[good_trs, ]
    # trim the data to the first good 123 TRs
    if (trimmed) {
        scan_data = scan_data[1:min(nrow(scan_data), 123),]
        imtrimmed = '_trimmed'
    } else {
        imtrimmed = ''
    }

    # scale it so that each time series has mean zero and SD 1
    scan_data = scale(scan_data)

    # setting up NIFTI file
    dims = c(ncol(scan_data), 1, 1, nrow(scan_data))
    arr = array(scan_data, dim=dims)
    nim = oro.nifti::nifti(arr)
    # converting to float32
    bitpix(nim) = 32
    datatype(nim) = 16
    out_fname = sprintf('%s/%s_%s%s', output_dir, m, p, imtrimmed)
    oro.nifti::writeNIfTI(nim, out_fname)

    all_scans = rbind(all_scans, scan_data)
}

# finish by creating a mask
dims = c(ncol(scan_data), 1, 1)
arr = array(1, dim=dims)
nim = oro.nifti::nifti(arr)
# converting to float32
bitpix(nim) = 32
datatype(nim) = 16
out_fname = sprintf('%s/mask_%s', output_dir, p)
oro.nifti::writeNIfTI(nim, out_fname)

# and spitting out the concatenated data
out_fname = sprintf('%s/tcat_%s.csv', output_dir, p)
write.csv(all_scans, file=out_fname, row.names=F)