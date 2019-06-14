# script to plot how much data is left in our fMRI data after using different
# cutoffs

fmriprep_dir = '/Volumes/Shaw/AROMA_ICA/fMRIprep_output/'
# maskids = c(362, 415, 423)
maskids = read.table('~/tmp/maskids.txt')[,1]  # single column of numbers
thresholds = c(1000, .8, .5, .2)
ntrs = 126

nmaskids = length(maskids)
nthresh = length(thresholds)

data = matrix(nrow=nmaskids, ncol=ntrs)

for (m in 1:nmaskids) {
    subj_dir = sprintf('%s/sub-%04d/fmriprep/sub-%04d/func/', fmriprep_dir,
                                                              maskids[m],
                                                              maskids[m])
    fname = sprintf('%s/sub-%04d_task-rest_run-1_desc-confounds_regressors.tsv',
                    subj_dir, maskids[m])
    scan_data = read.table(fname, header=1)
    data[m, 2:(ntrs-1)] = as.numeric(as.character(scan_data$framewise_displacement[2:(ntrs-1)]))
}

trs_left = matrix(nrow=nmaskids, ncol=nthresh)
for (t in 1:nthresh) {
    trs_left[, t] = rowSums(data < thresholds[t], na.rm=T)
}

mins_left = trs_left * 2.5 / 60
colnames(mins_left) = thresholds
rownames(mins_left) = maskids

library(gplots)
heatmap.2(mins_left, Colv=NA, dendrogram='none', trace='none', labCol='Scans')

# TODO
# - Add code to spit out a table with columns: threshold, min. time, nscans,
#   subj 2+, subj 3+, subj4+.