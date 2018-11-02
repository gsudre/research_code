# Makes a whole bunch of correlation matrices
#
# We assume that the directory structure is as follows: 
# input_dir > parcelation > subject > ROI.1D
# We also assume that all subjects have the same number of ROIs, even though
# some of the 1D files might be empty. Also, all 1D files for the same subject
# are assumed to have the same length. 
#
# GS, 11/2018


input_dir = '~/data/baseline_prediction/rsfmri/'
output_dir = '~/data/baseline_prediction/rsfmri/'
parc = c('aparc', 'aparc.a2009s')
trimmed = F  # whether to trim subjects with good TR > 123
methods = c('pearson', 'spearman', 'kendall')

for (me in methods) {
    for (p in parc) {
        print(sprintf('Working on %s, %s', p, me))
        # get labels but ignoring junk in beginnig and end of file
        roi_fname = sprintf('%s/%s+aseg_REN_all.niml.lt', input_dir, p)
        flen = length(readLines(roi_fname))
        roi_table = read.table(roi_fname, skip=4, nrows=(flen-7))

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
            rois = sapply(oneds, function(x) gsub('.1D', '', x))
            ntrs = sapply(oneds, function(x) length(readLines(sprintf('%s/%s',
                                                                    scan_dir, x))))
            scan_data = matrix(data=NA, nrow=max(ntrs), ncol=length(oneds))
            colnames(scan_data) = rois
            for (f in 1:length(oneds)) {
                # read in data for nonempty ROIs
                if (ntrs[f] > 0) {
                    scan_data[, rois[f]] = as.numeric(readLines(sprintf('%s/%s',
                                                                        scan_dir,
                                                                        oneds[f])))
                }
            }
            # remove any rows that are all zeros (censored TRs)
            good_rois = sum(ntrs>0)
            good_trs = rowSums(scan_data==0, na.rm=T) != good_rois
            scan_data = scan_data[good_trs, ]
            # trim the data to the first good 123 TRs
            if (trimmed) {
                scan_data = scan_data[1:min(nrow(scan_data), 123),]
                imtrimmed = '_trimmed'
            } else {
                imtrimmed = ''
            }
            combs = combn(1:length(rois), 2)
            corr_estimate = vector(mode='numeric', length=ncol(combs))
            corr_pval = vector(mode='numeric', length=ncol(combs))
            header = vector(mode='character', length=ncol(combs))
            for (k in 1:ncol(combs)) {
                roi_i = roi_table[roi_table[, 1] == rois[combs[1, k]], 2]
                roi_j = roi_table[roi_table[, 1] == rois[combs[2, k]], 2]
                header[k] = sprintf('%s_TO_%s', roi_i, roi_j)
                # only calculate correlation if one of the variables is not all NAs
                if (sum(is.na(scan_data[, combs[1, k]])) == nrow(scan_data) ||
                    sum(is.na(scan_data[, combs[2, k]])) == nrow(scan_data)) {
                    corr_estimate[k] = NA
                    corr_pval[k] = NA
                } else {
                    res = cor.test(scan_data[, combs[1, k]],
                                   scan_data[, combs[2, k]],
                                   method=me)
                    corr_estimate[k] = res$estimate
                    corr_pval[k] = res$p.value
                }
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
        write.csv(conn_raw, file=sprintf('%s/weighted_%s_%s%s.csv', output_dir,
                                         p, me, imtrimmed))
        write.csv(conn_pval, file=sprintf('%s/pvals_%s_%s%s.csv', output_dir,
                                         p, me, imtrimmed))
        write.csv(conn_p05, file=sprintf('%s/binaryP05_%s_%s%s.csv', output_dir,
                                         p, me, imtrimmed))
        write.csv(conn_fdr, file=sprintf('%s/binaryFDR05_%s_%s%s.csv', output_dir,
                                         p, me, imtrimmed))
    }
}