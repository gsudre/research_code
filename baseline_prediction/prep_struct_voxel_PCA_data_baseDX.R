qtile = .95
prop= 'volume'
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
adhd_clin = clin[clin$source != 'DICA_on', ]

qc_data = read.csv('~/data/baseline_prediction/struct_demo_withQC.csv')

# restrict based on QC
qc_vars = colnames(qc_data)[8:ncol(qc_data)] 
qc_data = qc_data[qc_data$"age_at_scan" < 17, ]

# for some reason we don't have volumne for 1875, so I'll exclude it from the
# get go. Or 1893.
qc_data = qc_data[qc_data$maskid != 1875, ]
qc_data = qc_data[qc_data$maskid != 1893, ]

# also, I have a few mask ids with more than one mprage. Ideally in the future
# we will only keep the one on which we ran Freesurfer for mriqc purposes. For
# now, since I don't know which one it was, I'll keep any single one, under the
# idea that if the person had more than one mprage it was bad to begin with.
qc_data = qc_data[!duplicated(qc_data$maskid), ]

# crop imaging data to only keep the people in adhd_clin!
df = mergeOnClosestDate(qc_data, adhd_clin,
                        unique(adhd_clin$MRN),
                         x.date='date_scan',
                         x.id='MRN')

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

# I created the huge brain data file with 641 scans following the instructions
# in the Freesurfer notes. Maybe it will include everyone that we will need, as
# it was created before QC. But we might need to recreate it later.
load(sprintf('~/data/baseline_prediction/lh.%s.ico4.gzip', prop))
lh_data = as.data.frame(data)
colnames(lh_data) = sapply(1:ncol(lh_data), function(x) sprintf('lh%04d', x))
load(sprintf('~/data/baseline_prediction/rh.%s.ico4.gzip', prop))
rh_data = as.data.frame(data)
colnames(rh_data) = sapply(1:ncol(rh_data), function(x) sprintf('rh%04d', x))
var_names = c(colnames(lh_data), colnames(rh_data))
slist = read.table('~/data/baseline_prediction/subjects_list.txt')[, 1]
brain_data = cbind(slist, lh_data, rh_data)
colnames(brain_data)[1] = 'maskid'
data = merge(df_clean, brain_data, by='maskid')

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
for (s in unique(data_clean$MRN)) {
    subj_idx = which(data_clean$MRN==s)
    subj_data = data_clean[subj_idx, ]
    dates = as.Date(as.character(subj_data$date_scan),
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

# Note that we do this even though we are assessing clinical status at the
# time, so that we can use the same dataset for within-ADHD predictions later

# run PCA-kaiser to get limits
# first remove voxels with zero variance
feat_var = apply(data_base_full[, var_names], 2, var, na.rm=TRUE)
idx = feat_var != 0
var_names_clean = var_names[idx]
# quick hack to use na.action on prcomp
fm_str = sprintf('~ %s', paste0(var_names_clean, collapse='+ ', sep=' '))
pca = prcomp(as.formula(fm_str), data_base_full[, var_names_clean], scale=T,
             na.action=na.exclude)
eigs <- pca$sdev^2
library(nFactors)
nS = nScree(x=eigs)
keep_me = 1:nS$Components$nkaiser
nondata = setdiff(colnames(data_base_full), var_names)
data_base = cbind(data_base_full[, nondata], data.frame(pca$x[, keep_me]))

# remember to keep the entire symptom history. This way we can compute slopes
# starting at the beginning, at current itme, and ending either one year later,
# or last observation. One year later only makes sense if starting at current
# time, though. So, we're talking about 3 continuous targets and 3 binary ones.

data_base[, 'adhdDX'] = NA
for (r in 1:nrow(data_base)) {
    subj = data_base[r,]$Medical.Record...MRN...Subjects
    subj_clin = adhd_clin[which(adhd_clin$MRN==subj), ]
    clin_dates = as.Date(as.character(subj_clin$DOA), format="%m/%d/%y")
    dob = as.Date(as.character(data_base[r, 'DOB']),
                  format="%m/%d/%Y")
    age_clinical = as.numeric((clin_dates - dob)/365.25)

    ordered_ages = sort(age_clinical, index.return=T)
    subj_clin = subj_clin[ordered_ages$ix, ]
    cur_age_clin = as.numeric((as.Date(as.character(data_base[r,]$DOA),
                                       format="%m/%d/%Y") - dob)/365.25)
    # in case there are duplicates, take the last one
    date_idx = max(which(ordered_ages$x==cur_age_clin))
    
    # strictly DSM5 categorization at the time of scan
    if ((subj_clin[date_idx, 'SX_inatt'] >= 6) ||
        (subj_clin[date_idx, 'SX_HI'] >= 6)) {
        data_base[r, 'adhdDX'] = 'improvers'  # just for back-compatibility
    } else {
        data_base[r, 'adhdDX'] = 'nonimprovers'
    }
}

out_fname = sprintf('~/data/baseline_prediction/struct_%s_PCA_OD%.2f_baseDX', prop, qtile)
write.csv(data_base, file=sprintf('%s.csv', out_fname), row.names=F, na='', 
          quote=F)
