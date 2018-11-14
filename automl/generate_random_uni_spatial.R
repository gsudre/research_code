# generates text files with results from univariate tests on randomized labels,
# to be later used to assess biggest cluster

args <- commandArgs(trailingOnly = TRUE)
data_fname = args[1]
clin_fname = args[2]
target = args[3]
myseed = as.numeric(args[4])

winsorize = function(x, cut = 0.01){
  cut_point_top <- quantile(x, 1 - cut, na.rm = T)
  cut_point_bottom <- quantile(x, cut, na.rm = T)
  i = which(x >= cut_point_top) 
  x[i] = cut_point_top
  j = which(x <= cut_point_bottom) 
  x[j] = cut_point_bottom
  return(x)
}

base_name = '~/data/'
print('Loading files')
# merging phenotype and clinical data
clin = read.csv(clin_fname)
load(data_fname)  #variable is data
x_orig = colnames(data)[grepl(pattern = '^v', colnames(data))]
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

input_target = target
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
if (myseed < 0) {
    # don't shuffle if seed is negative!
    myseed = -myseed
    idx = 1:nrow(df)
} else {
    set.seed(myseed)
    idx = sample(1:nrow(df), nrow(df), replace=F)
}
df[, target] = df[idx, target]

data.train = df

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
    ijk_fname = sprintf('%s/baseline_prediction/dti_223_ijk.txt', base_name)
    out_dir = sprintf('%s/tmp/', base_name)
    mask_fname = sprintf('%s/baseline_prediction/mean_223_fa_skeleton_mask.nii.gz',
                        base_name)
    out = read.table(ijk_fname)
    out[, 4] = 0
    out[keep_me, 4] = 1
    out_fname = sprintf('%s/%s_%d', out_dir, input_target, myseed)
    # writing good voxels to be clustered
    write.table(out, file=sprintf('%s.txt', out_fname), row.names=F, col.names=F)
    cmd_line = sprintf('cat %s.txt | 3dUndump -master %s -ijk -datum float -prefix %s -overwrite -;',
                        out_fname, mask_fname, out_fname)
    system(cmd_line)
    # spit out all clusters
    cmd_line = sprintf('3dclust -NN1 1 -orient LPI %s+orig 2>/dev/null > %s_rnd_clusters.txt',
                        out_fname, out_fname, out_fname)
    system(cmd_line)
} else if (grepl(pattern='struct', data_fname)) {
        # structural is a bit more challenging because left and right are separate
        nvox = length(x_orig)
        out_dir = sprintf('%s/tmp/', base_name)
        out = rep(0, nvox)
        names(out) = x_orig
        out[x[keep_me]] = 1
        out_fname = sprintf('%s/lh_%s_ds%d_%d', out_dir, input_target, f, myseed)

        # writing good voxels to be clustered. left hemisphere first
        write.table(out[1:(nvox/2)], file=sprintf('%s.txt', out_fname), row.names=F, col.names=F)
        
        # spit out all clusters >= min_cluster
        cmd_line = sprintf('SurfClust -i %s/freesurfer5.3_subjects/fsaverage/SUMA/lh.pial.asc -input %s.txt 0 -rmm -1.000000 -thresh_col 0 -athresh .95 -sort_area -no_cent -prefix %s_lh -out_roidset -out_fulllist -amm2 %s',
            base_name, out_fname, out_fname, min_clusters[[1]][f])
        system(cmd_line)
        # read mask back in and filter x properly
        clus = read.table(sprintf('%s_lh_ClstMsk_e1_a%s.0.niml.dset', out_fname, min_clusters[[1]][f]),
                        skip=12, nrows=(nvox/2))[[1]]
        lh_cluster_idx = clus > 0

        # let's average within each cluster, and only keep those variables as good
        my_clusters = unique(clus[lh_cluster_idx])
        new_x = c()
        x_lh = x_orig[grepl(pattern = 'lh', x_orig)]
        for (cl in 1:length(my_clusters)) {
            cluster_vars = clus == my_clusters[cl]
            cl_avg = rowMeans(data.train[, x_lh[cluster_vars]])
            data.train = cbind(data.train, cl_avg)
            colnames(data.train)[ncol(data.train)] = sprintf('v_ds%dLHclAvg%03d', f, cl)
            cl_avg = rowMeans(data.test[, x_lh[cluster_vars]])
            data.test = cbind(data.test, cl_avg)
            colnames(data.test)[ncol(data.test)] = sprintf('v_ds%dLHclAvg%03d', f, cl)
            new_x = c(new_x, sprintf('v_ds%dLHclAvg%03d', f, cl))
        }

        # now, repeat the exact same thing for right hemisphere
        out_fname = sprintf('%s/rh_%s_ds%d_%d', out_dir, input_target, f, myseed)

        write.table(out[(nvox/2+1):length(out)], file=sprintf('%s.txt', out_fname), row.names=F, col.names=F)
        cmd_line = sprintf('SurfClust -i %s/freesurfer5.3_subjects/fsaverage/SUMA/rh.pial.asc -input %s.txt 0 -rmm -1.000000 -thresh_col 0 -athresh .95 -sort_area -no_cent -prefix %s_rh -out_roidset -out_fulllist -amm2 %s',
            base_name, out_fname, out_fname, min_clusters[[1]][f])
        system(cmd_line)
        clus = read.table(sprintf('%s_rh_ClstMsk_e1_a%s.0.niml.dset', out_fname, min_clusters[[1]][f]),
                        skip=12, nrows=(nvox/2))[[1]]
        rh_cluster_idx = clus > 0

        my_clusters = unique(clus[rh_cluster_idx])
        x_rh = x_orig[grepl(pattern = 'rh', x_orig)]
        for (cl in 1:length(my_clusters)) {
            cluster_vars = clus == my_clusters[cl]
            cl_avg = rowMeans(data.train[, x_rh[cluster_vars]])
            data.train = cbind(data.train, cl_avg)
            colnames(data.train)[ncol(data.train)] = sprintf('v_ds%dRHclAvg%03d', f, cl)
            cl_avg = rowMeans(data.test[, x_rh[cluster_vars]])
            data.test = cbind(data.test, cl_avg)
            colnames(data.test)[ncol(data.test)] = sprintf('v_ds%dRHclAvg%03d', f, cl)
            new_x = c(new_x, sprintf('v_ds%dRHclAvg%03d', f, cl))
        }

        cluster_idx = c(lh_cluster_idx, rh_cluster_idx)
        print(sprintf('Variables after spatial filter: %d', sum(cluster_idx)))

        # disregard all other variables and keep only the cluster averages
        x = new_x
    }