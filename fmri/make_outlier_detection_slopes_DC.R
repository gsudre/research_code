qtile = .9
prop = 's' 
prop = 'sz'
voxdir = sprintf('~/data/heritability_change/%sdc_weighted/', prop)
out_fname = sprintf('~/data/heritability_change/rsfmri_%s_OD%.2f', prop, qtile)

demo = read.csv('~/data/heritability_change/resting_demo_07032019.csv')
cat(sprintf('Starting from %d scans\n', nrow(demo)))

# keeping it to kids only to make sure everyone has been processed
demo = demo[demo$age_at_scan < 18, ]
cat(sprintf('Down to %d to keep < 18 only\n', nrow(demo)))

# let's grab QC metrics on everyone
# note that this only works for non-censoring pipelines!
mydir = '/Volumes/Shaw/rsfmri_36P/xcpengine_output_fc-36p_despike/'
qc_data = c()
for (s in demo$Mask.ID) {
    subj = sprintf('sub-%04d', s)
    # if it processed all the way
    std_fname = sprintf('%s/%s/norm/%s_std.nii.gz', mydir, subj, subj)
    if (file.exists(std_fname)) {
        subj_data = read.csv(sprintf('%s/%s/%s_quality.csv', mydir, subj, subj))
        qc_data = rbind(qc_data, subj_data)
    }
}

cat(sprintf('Down to %d that have QC data\n', nrow(qc_data)))

# have some higly correlated qc variables, so let's remove the worse offenders (anything above abs(.8))
qc_vars = c('normCoverage', 'meanDV', 'pctSpikesDV',
            'motionDVCorrInit',
            'motionDVCorrFinal', "pctSpikesRMS", "relMeanRMSMotion")

library(solitude)
iso <- isolationForest$new()
iso$fit(qc_data[, qc_vars])
scores_if = as.matrix(iso$scores)[,3]

library(dbscan)
# here I set the number of neighbors to a percentage of the total data
scores_lof = lof(qc_data[, qc_vars], k = round(.5 * nrow(qc_data)))

thresh_lof = quantile(scores_lof, qtile)
thresh_if = quantile(scores_if, qtile)

idx = scores_lof < thresh_lof & scores_if < thresh_if

qc_data_clean = qc_data[idx, ]

cat(sprintf('Down to %d after removing QC outliers\n', nrow(qc_data_clean)))
net_dataP = c()
good_subjs = c()
for (s in qc_data_clean$id0) {
    m = as.numeric(gsub(s, pattern='sub-', replacement=''))
    fname = sprintf('%s/%sdc_%04d.txt', voxdir, prop, m)
    if (file.exists(fname)) {
        subj_data = read.table(fname)[, 4]
        net_dataP = rbind(net_dataP, subj_data)
        good_subjs = c(good_subjs, s)
    }
}
var_names = sapply(1:ncol(net_dataP), function(x) sprintf('v%06d', x))
colnames(net_dataP) = var_names
rownames(net_dataP) = good_subjs

cat(sprintf('Down to %d that have DC data\n', nrow(net_dataP)))

out_fname = sprintf('~/data/heritability_change/rsfmri_%sdcweighted_OD%.2f',
                    prop, qtile)

iso <- isolationForest$new()
iso$fit(as.data.frame(net_dataP[, var_names]))
scores_if = as.matrix(iso$scores)[,3]
scores_lof = lof(net_dataP[, var_names], k = round(.5 * nrow(net_dataP)))

thresh_lof = quantile(scores_lof, qtile)
thresh_if = quantile(scores_if, qtile)

idx = scores_lof < thresh_lof & scores_if < thresh_if
net_dataP = cbind(net_dataP, scores_lof)
colnames(net_dataP)[ncol(net_dataP)] = 'scores'
data = merge(qc_data_clean, net_dataP[idx,], by.x='id0', by.y=0)

cat(sprintf('Down to %d after QC on DC data\n', nrow(data)))

data$mask.id = as.numeric(gsub(data$id0, pattern='sub-', replacement=''))

df = merge(data, demo, by.x='mask.id', by.y='Mask.ID', all.x=T, all.y=F)

num_scans = 2  # number of scans to select

# removing people with less than num_scans scans
idx = which(table(df$Medical.Record...MRN)>=num_scans)
long_subjs = names(table(df$Medical.Record...MRN))[idx]
keep_me = c()
for (m in 1:nrow(df)) {
    if (df[m, ]$Medical.Record...MRN %in% long_subjs) {
        keep_me = c(keep_me, m)
    }
}
df = df[keep_me,]
cat(sprintf('Down to %d to keep only subjects with more than %d scans\n',
            nrow(df), num_scans))
keep_me = c()
for (s in unique(df$Medical.Record...MRN)) {
    found = F
    subj_idx = which(df$Medical.Record...MRN==s)
    subj_scans = df[subj_idx, ]
    dates = as.Date(as.character(subj_scans$"record.date.collected...Scan"),
                                    format="%m/%d/%Y")
    best_scans = sort(subj_scans$scores, index.return=T)
    # make sure they are at least 6 months apart. This is the idea:
    # grab the best X scans. Check the time difference between them.
    # Any time the time difference is not enough, remove the worse
    # scan and replace by the next in line. Keep doing this until
    # the time difference is enough between all scans, or we run out
    # of scans
    cur_scan = 1
    last_scan = num_scans
    cur_choice = best_scans$ix[cur_scan:last_scan]
    while (!found && last_scan <= nrow(subj_scans)) {
        time_diffs = abs(diff(dates[cur_choice]))
        if (all(time_diffs > 180)) {
            found = TRUE
        } else {
            # figure out which scan to remove. If there is more than one
            # to be removed, it will be taken care in the next iteration
            bad_diff = which.min(time_diffs)
            if (subj_scans$scores[cur_choice[bad_diff]] >
                subj_scans$scores[cur_choice[bad_diff + 1]]) {
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
        keep_me = c(keep_me, subj_idx[cur_choice])
    }
}
filtered_data = df[keep_me, ]

cat(sprintf('Down to %d to keep only two best scans per subject\n',
            nrow(filtered_data)))

source('~/research_code/lab_mgmt/merge_on_closest_date.R')
clin = read.csv('~/data/heritability_change/clinical_09182019.csv')
df = mergeOnClosestDate(filtered_data[, c('Medical.Record...MRN',
                                          'record.date.collected...Scan',
                                          'mask.id')],
                        clin,
                        unique(filtered_data$Medical.Record...MRN),
                         x.date='record.date.collected...Scan',
                         x.id='Medical.Record...MRN')
mres = merge(df, filtered_data, by='mask.id')
mres$SX_HI = as.numeric(as.character(mres$SX_hi))
mres$SX_inatt = as.numeric(as.character(mres$SX_inatt))
tract_names = var_names

# write.csv(df, file=sprintf('%s_twoTimePoints.csv', out_fname), row.names=F, na='', quote=F)

res = c()
for (s in unique(mres$Medical.Record...MRN.x)) {
    idx = which(mres$Medical.Record...MRN.x == s)
    row = c(s, unique(mres[idx, 'Sex']))
    y = mres[idx[2], c(tract_names, qc_vars)] - mres[idx[1], c(tract_names, qc_vars)]
    x = mres[idx[2], 'age_at_scan'] - mres[idx[1], 'age_at_scan']
    slopes = y / x
    row = c(row, slopes)
    for (t in c('SX_inatt', 'SX_HI')) {
        fm_str = sprintf('%s ~ age_at_scan', t)
        fit = lm(as.formula(fm_str), data=mres[idx, ], na.action=na.exclude)
        row = c(row, coefficients(fit)[2])
    }
    # grabbing inatt and HI at baseline
    base_DOA = which.min(mres[idx, 'age_at_scan'])
    row = c(row, mres[idx[base_DOA], 'SX_inatt'])
    row = c(row, mres[idx[base_DOA], 'SX_HI'])
    # DX1 is DSMV definition, DX2 will make SX >=4 as ADHD
    if (mres[idx[base_DOA], 'age_at_scan'] < 16) {
        if ((row[length(row)] >= 6) || (row[length(row)-1] >= 6)) {
            DX = 'ADHD'
        } else {
            DX = 'NV'
        }
    } else {
        if ((row[length(row)] >= 5) || (row[length(row)-1] >= 5)) {
            DX = 'ADHD'
        } else {
            DX = 'NV'
        }
    }
    if ((row[length(row)] >= 4) || (row[length(row)-1] >= 4)) {
        DX2 = 'ADHD'
    } else {
        DX2 = 'NV'
    }
    row = c(row, DX)
    row = c(row, DX2)
    res = rbind(res, row)
    print(nrow(res))
}
colnames(res) = c('ID', 'sex', tract_names, qc_vars, c('SX_inatt', 'SX_HI',
                                              'inatt_baseline',
                                              'HI_baseline',
                                              'DX', 'DX2'))
write.csv(res, file=sprintf('%s.csv', out_fname), row.names=F, na='', quote=F)

# data = read.csv(sprintf('%s.csv', out_fname))
# tmp = read.csv('~/data/heritability_change/pedigree.csv')
# data = merge(data, tmp[, c('ID', 'FAMID')], by='ID', all.x=T, all.y=F)
# related = names(table(data$FAMID))[table(data$FAMID) >= 2]
# keep_me = data$FAMID %in% related
# data2 = data[keep_me, ]
# write.csv(data2, file=sprintf('%s_Fam.csv', out_fname),
#           row.names=F, na='', quote=F)

# data = read.csv(sprintf('%s.csv', out_fname))

# iso <- isolationForest$new()
# iso$fit(as.data.frame(data[, tract_names]))
# scores_if = as.matrix(iso$scores)[,3]
# scores_lof = lof(data[, tract_names], k = round(.5 * nrow(data)))

# thresh_lof = quantile(scores_lof, qtile)
# thresh_if = quantile(scores_if, qtile)
# idx = scores_lof < thresh_lof & scores_if < thresh_if
# data2 = data[idx, ]
# write.csv(data2, file=sprintf('%s_QC.csv', out_fname),
#           row.names=F, na='', quote=F)
