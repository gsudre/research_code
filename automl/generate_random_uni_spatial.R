# generates text files with results from univariate tests on randomized labels,
# to be later used to assess biggest cluster

data_fname = '/data/NCR_SBRB/baseline_prediction/dti_ad_voxelwise_n223_09212018.RData.gz'
clin_fname = '/data/NCR_SBRB/baseline_prediction/long_clin_0918.csv'
target = 'nvVSper'
myseed = 42

print('Loading files')
# merging phenotype and clinical data
clin = read.csv(clin_fname)
load(data_fname)  #variable is data
# remove constant variables that screw up PCA and univariate tests
print('Removing constant variables')
feat_var = apply(data, 2, var, na.rm=TRUE)
idx = feat_var != 0  # TRUE for features with 0 variance (constant)
# categorical variables give NA variance, but we want to keep them
idx[is.na(idx)] = TRUE
data = data[, idx]
nNAs = colSums(is.na(data))  # number of NAs in each variable
# remove variables that are all NAs
data = data[, nNAs < nrow(data)]
print(sprintf('Features remaining: %d (%d with NAs)', ncol(data)-1, sum(nNAs>0)))
print('Merging files')
df = merge(clin, data, by='MRN')
print('Looking for data columns')
x = colnames(df)[grepl(pattern = '^v', colnames(df))]

# checking for subgroup analysis. Options are nonew_OLS_*_slope, nonew_diag_group2,
# ADHDonly_OLS_*_slope, ADHDonly_diag_group2, nonew_ADHDonly_*, ADHDNOS_OLS_*_slope,
# ADHDNOS_groupOLS_*_slope, nonew_ADHDNOS_*
# for pairwise, we can do the usual nvVSper, nvVSrem, perVSrem, then
# groupOLS_SX_slope_ plus nvVSimp, nvVSnonimp, impVSnonimp, plus all of them
# using nonew_
if (grepl('nonew', target)) {
  df = df[df$diag_group != 'new_onset', ]
  df$diag_group = factor(df$diag_group)
  target = sub('nonew_', '', target)
}
if (grepl('ADHDonly', target)) {
  df = df[df$diag_group != 'unaffect', ]
  df$diag_group = factor(df$diag_group)
  target = sub('ADHDonly_', '', target)
}
if (grepl('ADHDNOS', target)) {
  df = df[df$DX != 'NV', ]
  target = sub('ADHDNOS_', '', target)
  if (grepl('groupOLS', target) || grepl('grouprandom', target)) {
    df[, target] = 'nonimprovers'
    slope = sub('group', '', target)
    df[df[, slope] < 0, target] = 'improvers'
    df[, target] = as.factor(df[, target])
  }
}
# pairwise comparisons
if (grepl('VS', target)) {
    df[, 'groupSlope'] = 'nonimprovers'
    if (grepl('groupOLS', target)) {
        tmp = strsplit(target, '_')[[1]]
        slope_name = paste(tmp[1:(length(tmp)-1)], collapse='_')
        slope_name = sub('group', '', slope_name)
        df[df[, slope_name] < 0, 'groupSlope'] = 'improvers'
        if (grepl('nv', target)) {
            df[df$diag_group2 == 1, 'groupSlope'] = 'nv'
        }
        df$groupSlope = as.factor(df$groupSlope)
        target = tmp[length(tmp)]  # get the VS part only
    }
    groups = strsplit(target, 'VS')
    group1 = groups[[1]][1]
    group2 = groups[[1]][2]
    keep_me = F
    if (group1 == 'nv' || group2 == 'nv') {
        keep_me = keep_me | df$diag_group2 == 1
    }
    if (group1 == 'per' || group2 == 'per') {
        keep_me = keep_me | df$diag_group2 == 3
        target = 'diag_group2'
    }
    if (group1 == 'rem' || group2 == 'rem') {
        keep_me = keep_me | df$diag_group2 == 2
        target = 'diag_group2'
    }
    if (group1 == 'imp' || group2 == 'imp') {
        keep_me = keep_me | df$groupSlope == 'improvers'
        target = 'groupSlope'
    }
    if (group1 == 'nonimp' || group2 == 'nonimp') {
        keep_me = keep_me | df$groupSlope == 'nonimprovers'
        target = 'groupSlope'
    }
    if (group1 == 'adhd' || group2 == 'adhd') {
        df[df$diag_group2 == 3, 'diag_group2'] = 2
        keep_me = keep_me | df$diag_group2 == 2
        target = 'diag_group2'
    }
    # remove NVs if we are doing imp vs nonImp
    if (sum(keep_me) == nrow(df) && (grepl('imp', group1) || grepl('imp', group2))) {
        df = df[df$diag_group2 != 1, ]
    } else {
        df = df[keep_me, ]
    }
    df[, target] = as.factor(as.character(df[, target]))
    print(table(df[, target]))
}

# shuffling labels around
set.seed(myseed)
idx = sample(1:nrow(df), nrow(df), replace=F)
df[, target] = df[idx, target]

# set seed again to replicate old results
library(caret)
set.seed(myseed)
train_idx = sort(createDataPartition(df[, target], p = .9, list = FALSE, times = 1))
test_idx = sort(setdiff(1:nrow(df), train_idx)) # H2o only deals with sorted indexes
data.test = df[test_idx, ]
data.train = df[train_idx, ]
print(sprintf('Using %d samples for training + validation, %d for testing.',
              nrow(data.train),
              nrow(data.test)))

print('Running univariate analysis')
# winsorize and get univariates if it's a continuous variable
if (! grepl(pattern = 'group', target)) {
    b = sapply(data.train[, x],
                function(myx) {
                res = cor.test(myx, data.train[, target], method='spearman');
                return(res$p.value)
                })
    # winsorizing after correlations to avoid ties
    data.train[, target] = winsorize(data.train[, target])
    cut_point_top = max(data.train[, target])
    cut_point_bottom = min(data.train[, target])
    i = which(data.test[, target] >= cut_point_top) 
    data.test[i, target] = cut_point_top
    j = which(data.test[, target] <= cut_point_bottom) 
    data.test[j, target] = cut_point_bottom
} else {
    data.train[, target] = as.factor(data.train[, target])
    b = sapply(data.train[,x],
                function(myx) {
                res = kruskal.test(myx, data.train[, target]);
                return(res$p.value)
                })
}
keep_me = b <= .05
print(sprintf('Variables before univariate filter: %d', length(x)))
print(sprintf('Variables after univariate filter: %d', sum(keep_me)))

# further filter variables to keep only the ones clustered together
if (grepl(pattern='dti', data_fname)) {
    ijk_fname = '/data/NCR_SBRB/baseline_prediction/dti_223_ijk.txt'
    out_dir = '/data/NCR_SBRB/tmp/'
    mask_fname = '/data/NCR_SBRB/baseline_prediction/mean_223_fa_skeleton_mask.nii.gz'
    out = read.table(ijk_fname)
    out[, 4] = 0
    out[keep_me, 4] = 1
    out_fname = sprintf('%s/%s_%d', out_dir, target, myseed)
    # writing good voxels to be clustered
    write.table(out, file=sprintf('%s.txt', out_fname), row.names=F, col.names=F)
    cmd_line = sprintf('cat %s.txt | 3dUndump -master %s -ijk -datum float -prefix %s -overwrite -;',
                        out_fname, mask_fname, out_fname)
    system(cmd_line)
    # spit out all clusters
    cmd_line = sprintf('3dclust -NN1 1 -orient LPI %s+orig 2>/dev/null > %s_rnd_clusters.txt',
                        out_fname, out_fname, out_fname)
    system(cmd_line)
}