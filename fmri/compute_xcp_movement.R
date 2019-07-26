# calculates TRs left, mean FD and meanDVARS for only the TRs used in each
# pipeline
 
pipes = c('36P')#, '-p5', '-p5-nc', '-p25', '-p25-nc',
        #   '-gsr', '-gsr-p5', '-gsr-p5-nc', '-gsr-p25', '-gsr-p25-nc')

# grab all subjects
all_subjs = c()
for (p in pipes) {
    # mydir = sprintf('/Volumes/Shaw/AROMA_ICA/xcpengine_output_AROMA%s', p)
    mydir = '/Users/sudregp/data/36P/out/'
    cat(sprintf('Gathering subjects from %s\n', mydir))
    subjs = list.files(path=mydir)
    all_subjs = c(all_subjs, subjs)
}
all_subjs = all_subjs[grepl(all_subjs, pattern='^sub-')]
all_subjs = unique(all_subjs)

mycols = c('subj', 'pipeline', 'TRs_used', 'meanFD', 'meanDVARS',
           'fcon')
res = matrix(nrow=(length(all_subjs) * length(pipes)), ncol=length(mycols))
colnames(res) = mycols

r = 1
for (s in all_subjs) {
    cat(sprintf('Computing metrics for %s\n', s))
    for (p in pipes) {
        res[r, 'subj'] = s
        res[r, 'pipeline'] = p
        # mydir = sprintf('/Volumes/Shaw/AROMA_ICA/xcpengine_output_AROMA%s/%s',
        #                 p, s)
        mydir = sprintf('/Users/sudregp/data/36P/out/%s', s)
        fname = sprintf('%s/%s-nFlags.1D', mydir, s)
        if (file.exists(fname)) {
            censored = read.table(fname)[, 1]
            # when there's no censoring, nFlags is weird
            if (length(censored) == 1) {
                censored = rep(0, 126)
            }
            good_TRs = censored == 0
            res[r, 'TRs_used'] = sum(good_TRs)
            fname = sprintf('%s/prestats/%s_fmriconf.tsv', mydir, s)
            if (file.exists(fname)) {
                data = read.table(fname, header=1)
                # massaging to avoid first NA
                tmp = as.character(data[good_TRs, 'framewise_displacement'])
                res[r, 'meanFD'] = mean(as.numeric(tmp[2:length(tmp)]),
                                        na.rm=T)
                tmp = as.character(data[good_TRs, 'dvars'])
                res[r, 'meanDVARS'] = mean(as.numeric(tmp[2:length(tmp)]),
                                           na.rm=T)
            }
        }
        fname = sprintf('%s/fcon/power264/%s_power264.net', mydir, s)
        res[r, 'fcon'] = file.exists(fname)
        r = r + 1
    }
}
write.csv(res, file='~/data/tmp/xcp_movement.csv', row.names=F, quote=F)