qtile=.95
nvox=11990
prop='fa'
min_time = 30*9  # time between assessments in days

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

b = read.csv('/Volumes/Shaw/MasterQC/master_qc_20190314.csv')
a = read.csv('~/data/heritability_change/ready_1020.csv')
qc_data = merge(a, b, by.y='Mask.ID', by.x='Mask.ID...Scan', all.x=F)

# restrict based on QC
qc_vars = c("meanX.trans", "meanY.trans", "meanZ.trans",
            "meanX.rot", "meanY.rot", "meanZ.rot",
            "goodVolumes")
qc_data = qc_data[qc_data$"age_at_scan...Scan...Subjects" < 17, ]
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

dti_data = matrix(nrow=nrow(df_clean), ncol=nvox)
for (s in 1:nrow(dti_data)) {
    a = read.table(sprintf('~/data/baseline_prediction/dti_voxels/%04d_%s.txt',
                            df_clean[s,]$Mask.ID...Scan, prop))
    dti_data[s, ] = a[, 4]
}
var_names = sapply(1:nvox, function(x) sprintf('v%05d', x))
colnames(dti_data) = var_names
data = cbind(df_clean$Mask.ID...Scan, dti_data)
colnames(data)[1] = 'mask.id'

x = duplicated(data[, 'mask.id'])
data = merge(df_clean, data[!x, ], by.x='Mask.ID...Scan', by.y='mask.id')

iso <- isolationForest$new()
iso$fit(data[, var_names])
scores_if = as.matrix(iso$scores)[,3]
scores_lof = lof(data[, var_names], k = round(.5 * nrow(data)))

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
    if (sum((clin_dates - cur_clin) > min_time) > 0) {
        keep_me = c(keep_me, subj_idx[base_DOA])
    }
}
data_base_full = data_clean[keep_me, ]
cat(sprintf('Down to %d scans after keeping only baseline with future clinicals\n', nrow(data_base_full)))

# run PCA-kaiser to get limits
# quick hack to use na.action on prcomp
fm_str = sprintf('~ %s', paste0(var_names, collapse='+ ', sep=' '))
pca = prcomp(as.formula(fm_str), data_base_full[, var_names], scale=T,
             na.action=na.exclude)
eigs <- pca$sdev^2
library(nFactors)
nS = nScree(x=eigs)
keep_me = 1:nS$Components$nkaiser
nondata = setdiff(colnames(data_base_full), var_names)
data_base = cbind(data_base_full[, nondata], data.frame(pca$x[, keep_me]))

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
out_fname = sprintf('~/data/baseline_prediction/dti_%s_PCA_OD%.2f_DSM5Outcome', prop, qtile)
write.csv(data_base, file=sprintf('%s.csv', out_fname), row.names=F, na='', 
          quote=F)
