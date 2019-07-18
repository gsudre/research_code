# selects the best X scans for a subject across pipelines

# specify pipelines in order of most conservative ot less
pipelines = c('-p25', '-p5', '')
num_scans = 2  # number of scans to select

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

mvmt = read.csv('~/tmp/xcp_movement.csv')
# keep only pipeline records that went all the way through
mvmt = mvmt[mvmt$fcon, ]
maskids = sapply(mvmt$subj, function(x) as.numeric(gsub('sub-', '', x)))
mvmt$maskids = maskids
m = merge(a, mvmt, by.x='Mask.ID', by.y='maskids')
keep_me = c()
for (s in unique(m$Medical.Record...MRN)) {
    found = F
    cur_pipe = 1
    subj_idx = which(m$Medical.Record...MRN==s)
    subj_scans = m[subj_idx, ]
    while (!found && cur_pipe <= length(pipelines)) {
        # if subject has enough scans processed in this pipeline
        idx = which(subj_scans$pipeline == pipelines[cur_pipe])
        if (length(idx) >= num_scans) {
            pipe_scans = subj_scans[idx, ]
            dates = as.Date(as.character(pipe_scans$"record.date.collected...Scan"),
                                         format="%m/%d/%Y")
            best_scans = sort(pipe_scans$TRs_used, index.return=T,
                              decreasing=T)
            # make sure they are at least 6 months apart. This is the idea:
            # grab the best X scans. Check the time difference between them.
            # Any time the time difference is not enough, remove the worse
            # scan and replace by the next in line. Keep doing this until
            # the time difference is enough between all scans, or we run out
            # of scans
            cur_scan = 1
            last_scan = num_scans
            cur_choice = best_scans$ix[cur_scan:last_scan]
            while (!found && last_scan <= nrow(pipe_scans)) {
                time_diffs = abs(diff(dates[cur_choice]))
                if (all(time_diffs > 180)) {
                    found = TRUE
                } else {
                    # figure out which scan to remove. If there is more than one
                    # to be removed, it will be taken care in the next iteration
                    bad_diff = which.min(time_diffs)
                    if (pipe_scans$TRs_used[cur_choice[bad_diff]] <
                        pipe_scans$TRs_used[cur_choice[bad_diff + 1]]) {
                        rm_scan = cur_choice[bad_diff]
                    } else {
                        rm_scan = cur_choice[bad_diff + 1]
                    }
                    last_scan = last_scan + 1
                    if (last_scan <= nrow(pipe_scans)) {
                        cur_choice[cur_choice == rm_scan] = best_scans$ix[last_scan]
                    }
                }
            }
            if (!found) {
                cur_pipe = cur_pipe + 1
            } else {
                keep_me = c(keep_me, subj_idx[idx[cur_choice]])
            }
        } else {
            cur_pipe = cur_pipe + 1
        }
    }
}
filtered_data = m[keep_me, ]
filtered_data$pipeline = sapply(filtered_data$pipeline,
                                function(x) sprintf('"%s"', x))
write.csv(filtered_data, file='~/tmp/filtered.csv', row.names=F)