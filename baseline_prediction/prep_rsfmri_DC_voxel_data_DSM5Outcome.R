qtile = .95
prop = 's' 
# prop = 'sz'
voxdir = sprintf('~/data/heritability_change/%sdc_weighted/', prop)

min_time = 30*9  # time between assessments in days
with_qc = F

print(sprintf('Voxelwise %s with %f quantile OD', prop, qtile))

# the idea is to do this for voxel data, and then after we remove the bad scans
# we run a PCA in the entire clean dataset to summarize the data. I know we'd
# need to do this in a train/test split, but it's unsupervised and its's not
# that costly to always redo it. The size of our data also justifies it a bit,
# as it does make a difference adding a few more subjects.

source('~/research_code/lab_mgmt/merge_on_closest_date.R')

clin = read.csv('~/data/baseline_prediction/clinical_09182019_clean.csv')
# make sure the SX columns are numeric!
clin$SX_HI = as.numeric(as.character(clin$SX_hi))
clin$SX_inatt = as.numeric(as.character(clin$SX_inatt))
# let's remove on-medication items to not confuse the slopes
clin = clin[clin$source != 'DICA_on', ]

# we'll keep anyone that starts off with 6 or more symptoms, as dictated by DSM5
keep_me = c()
for (s in unique(clin$MRN)) {
    subj_idx = which(clin$MRN==s & !is.na(clin$SX_inatt) & !is.na(clin$SX_HI))
        if (length(subj_idx) > 0) {
        subj_data = clin[subj_idx, ]
        dates = as.Date(as.character(subj_data$DOA), format="%m/%d/%y")
        base_DOA = which.min(dates)
        if (subj_data[base_DOA,]$SX_HI >= 6 || subj_data[base_DOA,]$SX_inat >= 6) {
            keep_me = c(keep_me, subj_idx)
        }
    }
}
adhd_clin = clin[keep_me, ]

demo = read.csv('~/data/heritability_change/resting_demo_07032019.csv')
cat(sprintf('Starting from %d scans\n', nrow(demo)))

# keeping it to kids only to make sure everyone has been processed
demo = demo[demo$age_at_scan < 17, ]
cat(sprintf('Down to %d to keep < 17 only\n', nrow(demo)))

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

qc_data$mask.id = as.numeric(gsub(qc_data$id0, pattern='sub-', replacement=''))
qc_data = merge(qc_data, demo, by.x='mask.id', by.y='Mask.ID', all.x=T, all.y=F)

# have some higly correlated qc variables, so let's remove the worse offenders (anything above abs(.8))
qc_vars = c('normCoverage', 'meanDV', 'pctSpikesDV',
            'motionDVCorrInit',
            'motionDVCorrFinal', "pctSpikesRMS", "relMeanRMSMotion")

# crop imaging data to only keep the people in adhd_clin!
df = mergeOnClosestDate(qc_data, adhd_clin,
                        unique(adhd_clin$MRN),
                         x.date='record.date.collected...Scan',
                         x.id='Medical.Record...MRN')

cat(sprintf('Starting with %d scans after clinicals\n', nrow(df)))

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

net_dataP = c()
good_subjs = c()
for (s in df_clean$id0) {
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

iso <- isolationForest$new()
iso$fit(as.data.frame(net_dataP[, var_names]))
scores_if = as.matrix(iso$scores)[,3]
scores_lof = lof(net_dataP[, var_names], k = round(.5 * nrow(net_dataP)))

thresh_lof = quantile(scores_lof, qtile)
thresh_if = quantile(scores_if, qtile)

idx = scores_lof < thresh_lof & scores_if < thresh_if
net_dataP = cbind(net_dataP, scores_lof)
colnames(net_dataP)[ncol(net_dataP)] = 'scores'
data_clean = merge(df_clean, net_dataP[idx,], by.x='id0', by.y=0)

cat(sprintf('Down to %d after QC on DC data\n', nrow(data_clean)))

# choosing only baseline scan for each person, provided that they have a later
# clinical assessment. At this point, all scans are good, so it's OK to just
# choose baseline (provided that there are later clinical assessments)
keep_me = c()
for (s in unique(data_clean$Medical.Record...MRN)) {
    subj_idx = which(data_clean$Medical.Record...MRN==s)
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
    if (sum((clin_dates - cur_clin) > min_time) > 0) {
        keep_me = c(keep_me, subj_idx[base_DOA])
    }
}
data_base_full = data_clean[keep_me, ]
cat(sprintf('Down to %d scans after keeping only baseline with future clinicals\n', nrow(data_base_full)))

# changing variable names to make it easier to find them later
new_names = c()
for (v in colnames(data_base_full)) {
    if (v %in% var_names) {
        new_names = c(new_names, sprintf('v_%s', v))
    } else {
        new_names = c(new_names, v)
    }
}
colnames(data_base_full) = new_names
data_base = data_base_full

# remember to keep the entire symptom history. This way we can compute slopes
# starting at the beginning, at current itme, and ending either one year later,
# or last observation. One year later only makes sense if starting at current
# time, though. So, we're talking about 3 continuous targets and 3 binary ones.

data_base[, c('lastPersistent')] = NA
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
    
    if ((subj_clin[nrow(subj_clin), 'SX_inatt'] >= 6) ||
        (subj_clin[nrow(subj_clin), 'SX_HI'] >= 6)) {
        data_base[r, 'lastPersistent'] = 'improvers'  # just for back-compatibility
    } else {
        data_base[r, 'lastPersistent'] = 'nonimprovers'
    }
}

if (with_qc) {
    # change the names of QC variables, sex, and age to be included in
    # prediction
    for (v in c(qc_vars, 'age_at_scan...Scan...Subjects')) {
        cidx = which(colnames(data_base) == v)
        colnames(data_base)[cidx] = sprintf('v_%s', v)
    }
    # make sure all non-binary variables are in the same scale
    my_vars = grepl(colnames(data_base), pattern='^v_')
    data_base[my_vars] = scale(data_base[my_vars])
    data_base$v_isMale = 0
    data_base[data_base$Sex...Subjects == 'Male',]$v_isMale = 1 
    suffix = 'withQC_'
} else {
    suffix = ''
}
today = format(Sys.time(), "%m%d%Y")
out_fname = sprintf('~/data/baseline_prediction/rsfmri_%sDC_OD%.2f_DSM5Outcome_%s%s', prop,
                    qtile, suffix, today)
write.csv(data_base, file=sprintf('%s.csv', out_fname), row.names=F, na='', 
          quote=F)
