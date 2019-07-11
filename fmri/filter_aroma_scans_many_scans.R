pipelines = c('')#, '-gsr',
            #   '-p25', '-p5', '-gsr-p25', '-gsr-p5',
            #   '-gsr-p25-nc', '-gsr-p5-nc', '-p5-nc', '-p25-nc')
at_least_mins = c(0)#, 3, 4)  # needs to have at least these minutes of data
num_scans = 3  # number of scans to select

a = read.csv('~/data/heritability_change/resting_demo_07032019.csv')
cat(sprintf('Starting from %d scans\n', nrow(a)))
# remove adults and subjects with a single scan. This way we make sure everything for this study was processed
a = a[a$age_at_scan < 18, ]
cat(sprintf('Down to %d to keep < 18 only\n', nrow(a)))
a = a[a$processed_AROMA == 'TRUE', ]
cat(sprintf('Down to %d to keep only scans that have been processed\n', nrow(a)))
# removing people with less than num_scans scans
idx = which(table(a$Medical.Record...MRN)>=num_scans)
long_subjs = names(table(a$Medical.Record...MRN))[idx]
keep_me = c()
for (m in 1:nrow(a)) {
    if (a[m, ]$Medical.Record...MRN %in% long_subjs) {
        keep_me = c(keep_me, m)
    }
}
a = a[keep_me,]
cat(sprintf('Down to %d to keep only subjects with more than %d scans\n',
            nrow(a), num_scans))
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
        m = merge(aGood, data, by='Mask.ID', all.x=F)
        cat(sprintf('\t\tDown to %d scans with connectivity data\n', nrow(m)))

        # keeping only the two best scans for each subject, at least 6 months apart
        keep_me = c()
        cnt = 1
        for (s in unique(m$Medical.Record...MRN)) {
            cat(sprintf('\t\t\tSubject %d/%d\n',
                        cnt, length(unique(m$Medical.Record...MRN))))
            subj_scans = m[m$Medical.Record...MRN==s, ]
            dates = as.Date(as.character      (subj_scans$"record.date.collected...Scan"),
                                        format="%m/%d/%Y")
            # assumes we only have people with at least num_scans scans!
            best_scans = sort(subj_scans$goodness, index.return=T)
            # make sure they are at least 6 months apart. This is the idea:
            # grab the best X scans. Check the time difference between them.
            # Any time the time difference is not enough, remove the worse
            # scan and replace by the next in line. Keep doing this until
            # the time difference is enough between all scans, or we run out
            # of scans
            cur_scan = 1
            last_scan = num_scans
            cur_choice = best_scans$ix[cur_scan:last_scan]
            found = FALSE
            while (!found && last_scan <= nrow(subj_scans)) {
                time_diffs = abs(diff(dates[cur_choice]))
                if (all(time_diffs > 180)) {
                    found = TRUE
                } else {
                    # figure out which scan to remove. If there is more than one
                    # to be removed, it will be taken care in the next iteration
                    bad_diff = which.min(time_diffs)
                    if (subj_scans$goodness[cur_choice[bad_diff]] >
                        subj_scans$goodness[cur_choice[bad_diff + 1]]) {
                        rm_scan = cur_choice[bad_diff]
                    } else {
                        rm_scan = cur_choice[bad_diff + 1]
                    }
                    last_scan = last_scan + 1
                    if (last_scan <= nrow(subj_scans)) {
                        cur_choice[cur_choice == rm_scan] = best_scans$ix[last_scan]
                    }
                }
            }
            if (found) {
                keep_me = c(keep_me, subj_scans[cur_choice]))
            }
            cnt = cnt + 1
        }
        a2Good = m[keep_me, ]
        cat(sprintf('\t\tDown to %d scans only keeping %d best ones 6-mo apart\n',
                    nrow(a2Good), num_scans))

        good_na_conns = rowSums(is.na(a2Good))
        for (sc in which(good_na_conns > 1500)) {
            cat(sprintf('WARNING!!! Scan %04d has %d uncovered connections (%.2f %%)\n',
                        a2Good[sc, 'Mask.ID'], good_na_conns[sc], good_na_conns[sc]/nconn*100))
        }

        fname = sprintf('~/data/heritability_change/rsfmri_AROMA%s_%dmin_best%dscans.csv',
                        p, min_time, num_scans)
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
        fname = sprintf('~/data/heritability_change/rsfmri_AROMA%s_%dmin_best%dscansFams.csv',
                        p, min_time, num_scans)
        write.csv(a2GoodFam, file=fname, row.names=F, na='', quote=F)
    }
}
