# calculates TRs left, mean FD and meanDVARS for only the TRs used in each
# pipeline
 
# pipes = c('', '-p5', '-p5-nc', '-p25', '-p25-nc',
#           '-gsr', '-gsr-p5', '-gsr-p5-nc', '-gsr-p25', '-gsr-p25-nc')
# pipes = c('fc-36p_despike', 'fc-36p', 'fc-36p_scrub_p25', 'fc-36p_scrub_p5',
#           'fc-36p_spkreg')

pipes = c('AROMA', 'AROMA-p5', 'AROMA-p5-nc', 'AROMA-p25', 'AROMA-p25-nc',
          'AROMA-gsr', 'AROMA-gsr-p5', 'AROMA-gsr-p5-nc',
          'AROMA-gsr-p25', 'AROMA-gsr-p25-nc',
          'fc-36p_despike', 'fc-36p', 'fc-36p_scrub_p25', 'fc-36p_scrub_p5',
          'fc-36p_spkreg')

# grab all subjects
all_subjs = c()
for (p in pipes) {
    mydir = sprintf('/data/NCR_SBRB/xcpengine_output_%s', p)
    cat(sprintf('Gathering subjects from %s\n', mydir))
    subjs = list.files(path=mydir)
    all_subjs = c(all_subjs, subjs)
}
all_subjs = all_subjs[grepl(all_subjs, pattern='^sub-')]
all_subjs = unique(all_subjs)

mycols = c('subj', 'pipeline', 'TRs_used', 'meanFD', 'meanDVARS',
           'power264')
res = matrix(nrow=(length(all_subjs) * length(pipes)), ncol=length(mycols))
colnames(res) = mycols

r = 1
for (s in all_subjs) {
    cat(sprintf('Computing metrics for %s\n', s))
    for (p in pipes) {
        res[r, 'subj'] = s
        res[r, 'pipeline'] = p
        mydir = sprintf('/data/NCR_SBRB/xcpengine_output_%s/%s', p, s)
        fname = sprintf('%s/%s-nFlags.1D', mydir, s)
        if (file.exists(fname)) {
            censored = read.table(fname)[, 1]
            fname = sprintf('%s/prestats/%s_fmriconf.tsv', mydir, s)
            if (file.exists(fname)) {
                data = read.table(fname, header=1)

                # for some pipelines that don't need censoring xcpengine still
                # makes a healthy nFlags file, so we need to identify those
                # pipelines and skip their nFlags!
                orig_TRs = nrow(data)
                fname = sprintf('%s/qcfc/%s_dvars-raw.1D', mydir, s)
                junk = read.table(fname)[, 1]
                used_TRs = length(junk)
                if (used_TRs == orig_TRs) {
                    censored = rep(0, orig_TRs)
                }
                
                good_TRs = censored == 0
                res[r, 'TRs_used'] = sum(good_TRs)
                
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
        res[r, 'power264'] = file.exists(fname)
        r = r + 1
    }
}
write.csv(res, file='~/data/tmp/xcp_movement.csv', row.names=F, quote=F)