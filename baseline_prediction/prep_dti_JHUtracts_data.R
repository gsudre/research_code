qtile=.95

source('~/research_code/lab_mgmt/merge_on_closest_date.R')

clin = read.csv('~/data/baseline_prediction/clinical_09182019_clean.csv')
# make sure the SX columns are numeric!
clin$SX_HI = as.numeric(as.character(clin$SX_hi))
clin$SX_inatt = as.numeric(as.character(clin$SX_inatt))

# we'll keep anyone that starts off with 4 or more symptoms
keep_me = c()
for (s in unique(clin$MRN)) {
    subj_idx = which(clin$MRN==s & !is.na(clin$SX_inatt) & !is.na(clin$SX_HI))
        if (length(subj_idx) > 0) {
        subj_data = clin[subj_idx, ]
        dates = as.Date(as.character(subj_data$DOA), format="%m/%d/%y")
        base_DOA = which.min(dates)
        if (subj_data[base_DOA,]$SX_HI >= 4 || subj_data[base_DOA,]$SX_inat >= 4) {
            keep_me = c(keep_me, subj_idx)
        }
    }
}
adhd_clin = clin[keep_me, ]

b = read.csv('/Volumes/Shaw/MasterQC/master_qc_20190314.csv')
a = read.csv('~/data/heritability_change/ready_1020.csv')
qc_data = merge(a, b, by.y='Mask.ID', by.x='Mask.ID...Scan', all.x=F)

# restrict based on QC
qc_vars = c("meanX.trans", "meanY.trans", "meanZ.trans",
            "meanX.rot", "meanY.rot", "meanZ.rot",
            "goodVolumes")
qc_data = qc_data[qc_data$"age_at_scan...Scan...Subjects" < 18, ]
qc_data = qc_data[qc_data$"goodVolumes" <= 61, ]
qc_data = qc_data[qc_data$"numVolumes" < 80, ]

# crop imaging data to only keep the people in adhd_clin!
df = mergeOnClosestDate(qc_data, adhd_clin,
                        unique(adhd_clin$MRN),
                         x.date='record.date.collected...Scan',
                         x.id='Medical.Record...MRN...Subjects')

cat(sprintf('Starting with %d scans\n', nrow(df)))

library(solitude)
iso <- isolationForest$new()
iso$fit(df[, qc_vars])
scores_if = as.matrix(iso$scores)[,3]
library(dbscan)
# here I set the number of neighbors to a percentage of the total data
scores_lof = lof(df[, qc_vars], k = round(.5 * nrow(df)))

thresh_lof = quantile(scores_lof, qtile)
thresh_if = quantile(scores_if, qtile)
idx = scores_lof < thresh_lof & scores_if < thresh_if
df_clean = df[idx,]

cat(sprintf('Down to %d scans after removing on QC variables\n', nrow(df_clean)))

tracts = read.csv('~/data/baseline_prediction/jhu_tracts_1020.csv')
# somehow I have two entries for 1418?
x = duplicated(tracts$id)
data = merge(df_clean, tracts[!x, ], by.x='Mask.ID...Scan', by.y='id')
tract_names = colnames(tracts)[grepl(colnames(tracts), pattern="^ad") | 
                                grepl(colnames(tracts), pattern="^rd")]

iso <- isolationForest$new()
iso$fit(data[, tract_names])
scores_if = as.matrix(iso$scores)[,3]
scores_lof = lof(data[, tract_names], k = round(.5 * nrow(data)))

thresh_lof = quantile(scores_lof, qtile)
thresh_if = quantile(scores_if, qtile)
idx = scores_lof < thresh_lof & scores_if < thresh_if
data_clean = data[idx, ]

cat(sprintf('Down to %d scans after removing on data QC\n', nrow(data_clean)))

# choosing only baseline scan for each person, provided that they have a later
# clinical assessment. At this point, all scans are good, so it's OK to just
# choose baseline (provided that there are later clinical assessments)
keep_me = c()
for (s in unique(data_clean$Medical.Record...MRN...Subjects)) {
    subj_idx = which(data_clean$Medical.Record...MRN...Subjects==s)
    subj_data = data_clean[subj_idx, ]
    dates = as.Date(as.character(subj_data$record.date.collected...Scan),
                    format="%m/%d/%Y")
    base_DOA = which.min(dates)
    subj_clin = adhd_clin[which(adhd_clin$MRN==s), ]
    clin_dates = as.Date(as.character(subj_clin$DOA), format="%m/%d/%y")
    # make sure we have at least one clinical date at least 9 months apart from
    # the currently matched clinical date!
    cur_clin = as.Date(as.character(subj_data[base_DOA,]$DOA),
                       format="%m/%d/%Y")
    if (sum((clin_dates - cur_clin) > 30*9) > 0) {
        keep_me = c(keep_me, subj_idx[base_DOA])
    }
}
data_base = data_clean[keep_me, ]
cat(sprintf('Down to %d scans after keeping only baseline with future clinicals\n', nrow(data_base)))

# remember to keep the entire symptom history. This way we can compute slopes
# starting at the beginning, at current itme, and ending either one year later,
# or last observation. One year later only makes sense if starting at current
# time, though. So, we're talking about 3 continuous targets and 3 binary ones.

data_base[, c('SX_HI_slopeNext', 'SX_inatt_slopeNext',
              'SX_HI_slopeLast', 'SX_inatt_slopeLast',
              'SX_HI_slopeStudy', 'SX_inatt_slopeStudy')] = NA
for (r in 1:nrow(data_base)) {
    subj = data_base[r,]$Medical.Record...MRN...Subjects
    subj_clin = adhd_clin[which(adhd_clin$MRN==subj), ]
    clin_dates = as.Date(as.character(subj_clin$DOA), format="%m/%d/%y")
    dob = as.Date(as.character(data_base[r, 'Date.of.Birth...Subjects']),
                  format="%m/%d/%Y")
    age_clinical = as.numeric((clin_dates - dob)/365.25)

    ordered_ages = sort(age_clinical, index.return=T)
    subj_clin = subj_clin[ordered_ages$ix, ]
    cur_age_clin = as.numeric((as.Date(as.character(data_base[r,]$DOA),
                                       format="%m/%d/%Y") - dob)/365.25)
    # in case there are duplicates, take the last one
    date_idx = max(which(ordered_ages$x==cur_age_clin))
        
    for (t in c('SX_inatt', 'SX_HI')) {
        # the easiest one is overall study slope
        fm_str = sprintf('%s ~ age_clinical', t)
        fit = lm(as.formula(fm_str), data=subj_clin, na.action=na.exclude)
        data_base[r, sprintf('%s_slopeStudy', t)] = coefficients(fit)[2]

        slope = ((subj_clin[date_idx + 1, t] - subj_clin[date_idx, t]) / 
                 (ordered_ages$x[date_idx + 1] - ordered_ages$x[date_idx]))
        data_base[r, sprintf('%s_slopeNext', t)] = slope

        slope = ((subj_clin[nrow(subj_clin), t] - subj_clin[date_idx, t]) / 
                 (ordered_ages$x[nrow(subj_clin)] - ordered_ages$x[date_idx]))
        data_base[r, sprintf('%s_slopeLast', t)] = slope
    }
}
for (s in c('Next', 'Last', 'Study')) {
    for (t in c('SX_inatt', 'SX_HI')) {
        data_base[, sprintf('%s_group%s', t, s)] = NA
        idx = data_base[, sprintf('%s_slope%s', t, s)] < 0
        data_base[idx, sprintf('%s_group%s', t, s)] = 'improvers'
        data_base[!idx, sprintf('%s_group%s', t, s)] = 'nonimprovers'
    }
}
out_fname = sprintf('~/data/baseline_prediction/dti_JHUtracts_ADRDonly_OD%.2f', qtile)
write.csv(df, file=sprintf('%s.csv', out_fname), row.names=F, na='', quote=F)
