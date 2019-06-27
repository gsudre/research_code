pipelines = c('-gsr-p25', '-gsr-p5')
at_least_mins = c(0, 3, 4)  # needs to have at least these minutes of data

a = read.csv('~/data/heritability_change/resting_demo_06262019.csv')
cat(sprintf('Starting from %d scans\n', nrow(a)))
# remove adults and subjects with a single scan. This way we make sure everything for this study was processed
a = a[a$age_at_scan < 18, ]
cat(sprintf('Down to %d to keep < 18 only\n', nrow(a)))
a = a[a$processed_AROMA == 'TRUE', ]
cat(sprintf('Down to %d to keep only scans that have been processed\n', nrow(a)))
idx = which(table(a$Medical.Record...MRN)>1)
long_subjs = names(table(a$Medical.Record...MRN))[idx]
keep_me = c()
for (m in 1:nrow(a)) {
    if (a[m, ]$Medical.Record...MRN %in% long_subjs) {
        keep_me = c(keep_me, m)
    }
}
a = a[keep_me,]
cat(sprintf('Down to %d to keep only subjects with more than 1 scan\n', nrow(a)))
for (p in pipelines) {
    pipe_dir = sprintf('/data/NCR_SBRB/xcpengine_output_AROMA%s/', p)
    cat(sprintf('Reading quality data from %s\n', pipe_dir))
    outliers = c()
    goodness = c()
    # reading quality metric for all scans
    for (m in a$Mask.ID) {
        fname = sprintf('%s/sub-%04d/sub-%04d_quality.csv', pipe_dir, m, m)
        qual = read.csv(fname)
        if (sum(names(qual)=='nVolCensored') == 0) {
            outliers = c(outliers, 0)
        }
        else {
            outliers = c(outliers, qual$nVolCensored)
        }
        # need to use a quality metric that works in all pipelines, regardless of censoring!
        if (sum(names(qual)=='relMeanRMSMotion') == 0) {
            cat(sprintf('WARNING!!! No relMeanRMSMotion for scan %04d!\n', m))
            goodness = c(goodness, 1000)
        }
        else {
            goodness = c(goodness, qual$relMeanRMSMotion)
        }
    }
    a$outliers = outliers
    a$goodness = goodness

    cat('Loading connectivity data...\n')
    nconn = 34716
    data = matrix(nrow=nrow(a), ncol=nconn)
    for (m in 1:nrow(data)) {
        fname = sprintf('%s/sub-%04d/fcon/power264/sub-%04d_power264_network.txt',
                        pipe_dir, a[m,]$Mask.ID, a[m,]$Mask.ID)
        if (file.exists(fname)) {
            data[m, ] = read.table(fname)[,1]
        }
    }
    data = cbind(a$Mask.ID, data)
    # remove scans that are NAs for all connections
    na_conns = rowSums(is.na(data))
    colnames(data) = c('Mask.ID', sapply(1:nconn, function(x) sprintf('conn%d', x)))

    data = data[na_conns < nconn, ]
    # only keep scans with at least some amount of time
    for (min_time in at_least_mins) {
        uncensored_time = (125 - a$outliers) * 2.5 / 60
        aGood = a[uncensored_time > min_time, ]
        cat(sprintf('\tDown to %d scans with good %d minutes\n', nrow(aGood),
                                                                 min_time))

        # merge the data so we can remove subjects with not enough time DOF
        m = merge(aGood, data, by='Mask.ID', all.x=T)
        cat(sprintf('\t\tDown to %d scans with connectivity data\n', nrow(m)))

        # keeping only the two best scans for each subject, at least 6 months apart
        keep_me = c()
        for (s in unique(m$Medical.Record...MRN)) {
            subj_scans = m[m$Medical.Record...MRN==s, ]
            dates = as.Date(as.character(subj_scans$"record.date.collected...Scan"),
                                        format="%m/%d/%Y")
            if (length(dates) >= 2) {
                best_scans = sort(subj_scans$goodness, index.return=T)
                # make sure there is at least 6 months between scans
                next_scan = 2
                while ((abs(dates[best_scans$ix[next_scan]] - dates[best_scans$ix[1]]) < 180) &&
                        (next_scan < length(dates))) {
                    next_scan = next_scan + 1
                }
                if (abs(dates[best_scans$ix[next_scan]] - dates[best_scans$ix[1]]) > 180) {
                    idx1 = best_scans$ix[1]
                    keep_me = c(keep_me, which(m$Mask.ID == subj_scans[idx1, 'Mask.ID']))
                    idx2 = best_scans$ix[next_scan]
                    keep_me = c(keep_me, which(m$Mask.ID == subj_scans[idx2, 'Mask.ID']))
                }
            }
        }
        a2Good = m[keep_me, ]
        cat(sprintf('\t\tDown to %d scans only keeping two best ones 6-mo apart\n',
                    nrow(a2Good)))

        good_na_conns = rowSums(is.na(a2Good))
        for (sc in which(good_na_conns > 1500)) {
            cat(sprintf('WARNING!!! Scan %04d has %d uncovered connections (%.2f %%)\n',
                        a2Good[sc, 'Mask.ID'], good_na_conns[sc], good_na_conns[sc]/nconn*100))
        }

        fname = sprintf('~/data/heritability_change/rsfmri_AROMA%s_%dmin_best2scans.csv',
                        p, min_time)
        write.csv(a2Good, file=fname, row.names=F, na='', quote=F)
        # make sure every family has at least two people
        idx = table(a2Good$Nuclear.ID...FamilyIDs) >= 4
        good_nuclear = names(table(a2Good$Nuclear.ID...FamilyIDs))[idx]
        idx = table(a2Good$Extended.ID...FamilyIDs) >= 4
        good_extended = names(table(a2Good$Extended.ID...FamilyIDs))[idx]
        keep_me = c()
        for (f in good_nuclear) {
            keep_me = c(keep_me, a2Good[which(a2Good$Nuclear.ID...FamilyIDs == f),
                                    'Medical.Record...MRN'])
        }
        for (f in good_extended) {
            keep_me = c(keep_me, a2Good[which(a2Good$Extended.ID...FamilyIDs == f),
                                    'Medical.Record...MRN'])
        }
        keep_me = unique(keep_me)

        fam_subjs = c()
        for (s in keep_me) {
            fam_subjs = c(fam_subjs, which(a2Good[, 'Medical.Record...MRN'] == s))
        }
        a2GoodFam = a2Good[fam_subjs, ]
        cat(sprintf('\t\tDown to %d scans only keeping families\n',
                    nrow(a2GoodFam)))
        fname = sprintf('~/data/heritability_change/rsfmri_AROMA%s_%dmin_best2scansFams.csv',
                        p, min_time)
        write.csv(a2GoodFam, file=fname, row.names=F, na='', quote=F)
    }
}