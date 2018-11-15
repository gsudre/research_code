# Makes a whole bunch of partial correlation matrices
#
# We assume that the directory structure is as follows: 
# input_dir > parcelation > subject > ROI.1D
# We also assume that all subjects have the same number of ROIs, even though
# some of the 1D files might be empty. Also, all 1D files for the same subject
# are assumed to have the same length. 
#
# This script is similar to make_all_correlations.R in many ways, except that
# when calculating partial correlations we need to pay attention to certain
# things that we didn't need to worry about before. For example:
#  - we need more TRs than ROIs, which removes aparc.a2009s for most of subjects
#  - we cannot handle missing rois
#
# GS, 11/2018


input_dir = '~/data/baseline_prediction/rsfmri/'
output_dir = '~/data/baseline_prediction/rsfmri/'
trimmed = F  # whether to trim subjects with good TR > 123
methods = c('pearson', 'spearman', 'kendall')
p = 'aparc'

# some non-grey mater ROIs we don't need
rm_rois = c('CSF', 'Ventricle$', 'Pallidum$', 'Brain.Stem',
            'Accumbens.area$', 'VentralDC$', 'vessel$', 'Cerebral',
            'choroid', 'Lat.Vent$', 'White.Matter$', 'hypointensities',
            '^CC', 'nknown$', 'Chiasm$', 'Cerebellum.Cortex$')
# some extra subcortical stuff just so we can have less ROIs compared to
# uncensored TRs
rm_rois = c(rm_rois, 'Thalamus-Proper$', 'Caudate$', 'Putamen$', 'Hippocampus$',
            'Amygdala$')

library(ppcor)

for (me in methods) {
    print(sprintf('Working on %s, %s', me, p))
    # get labels but ignoring junk in beginnig and end of file
    roi_fname = sprintf('%s/%s+aseg_REN_all.niml.lt', input_dir, p)
    flen = length(readLines(roi_fname))
    roi_table = read.table(roi_fname, skip=4, nrows=(flen-7))

    rm_me = c()
    for (r in rm_rois) {
        rm_me = c(rm_me, which(grepl(r, roi_table[, 2])))
    }
    roi_table = roi_table[-rm_me, ]

    # get list of subjects from directory
    maskids = list.files(path=sprintf('%s/%s/', input_dir, p), pattern='*')
    conn_raw = c()
    conn_pval = c()
    conn_p05 = c()
    conn_fdr = c()
    for (m in maskids) {
        print(m)
        scan_dir = sprintf('%s/%s/%s/', input_dir, p, m)
        oneds = list.files(path=scan_dir, pattern='*.1D')
        ntrs = sapply(oneds, function(x) length(readLines(sprintf('%s/%s',
                                                                scan_dir, x))))
        # only grabing data for ROIs that we want to include
        scan_data = matrix(data=NA, nrow=max(ntrs), ncol=nrow(roi_table))
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

        combs = combn(1:ncol(scan_data), 2)
        if (nrow(scan_data) > ncol(scan_data)) {
            corr_estimate = vector(mode='numeric', length=ncol(combs))
            corr_pval = vector(mode='numeric', length=ncol(combs))
            header = vector(mode='character', length=ncol(combs))
            for (k in 1:ncol(combs)) {
                roi_i = colnames(scan_data)[combs[1, k]]
                roi_j = colnames(scan_data)[combs[2, k]]
                header[k] = sprintf('%s_TO_%s', roi_i, roi_j)
                # only calculate correlation if one of the variables is not all NAs
                if (sum(is.na(scan_data[, roi_i])) == nrow(scan_data) ||
                    sum(is.na(scan_data[, roi_j])) == nrow(scan_data)) {
                    corr_estimate[k] = NA
                    corr_pval[k] = NA
                } else {
                    # the variables to condition the correlation cannot be X, Y, or
                    # NAs 
                    nuisance = scan_data[, setdiff(colnames(scan_data), c(roi_i, roi_j))]
                    good_rois = colSums(is.na(nuisance)) != nrow(nuisance)
                    nuisance = nuisance[, good_rois]
                    res = pcor.test(scan_data[, roi_i],
                                    scan_data[, roi_j],
                                    nuisance, method=me)
                    corr_estimate[k] = res$estimate
                    corr_pval[k] = res$p.value
                }
            }
        } else {
            print(sprintf('Not enough TRs to compute partial correlation. Have %d, need more than %d',
                          nrow(scan_data), ncol(scan_data)))
            corr_estimate = rep(NA, length=ncol(combs))
            corr_pval = rep(1, length=ncol(combs))
        }
        conn_raw = rbind(conn_raw, corr_estimate)
        conn_pval = rbind(conn_pval, corr_pval)
        tmp = rep(0, length(corr_estimate))
        tmp[corr_pval < .05] = 1
        conn_p05 = rbind(conn_p05, tmp)
        tmp = rep(0, length(corr_estimate))
        pval2 = p.adjust(corr_pval, method='fdr')
        tmp[pval2 < .05] = 1
        conn_fdr = rbind(conn_fdr, tmp)
    }
    rownames(conn_raw) = maskids
    colnames(conn_raw) = header
    rownames(conn_pval) = maskids
    colnames(conn_pval) = header
    rownames(conn_p05) = maskids
    colnames(conn_p05) = header
    rownames(conn_fdr) = maskids
    colnames(conn_fdr) = header
    write.csv(conn_raw, file=sprintf('%s/partial_weighted_%s%s.csv', output_dir,
                                     me, imtrimmed))
    write.csv(conn_pval, file=sprintf('%s/partial_pval_%s%s.csv', output_dir,
                                     me, imtrimmed))
    write.csv(conn_p05, file=sprintf('%s/partial_binaryP05_%s%s.csv', output_dir,
                                     me, imtrimmed))
    write.csv(conn_fdr, file=sprintf('%s/partial_binaryFDR05_%s%s.csv', output_dir,
                                     me, imtrimmed))
}