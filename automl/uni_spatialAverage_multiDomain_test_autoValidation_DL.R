# runs classification tasks using AutoML from H2O. Using test set, spatial
# filter on clusters, average of clusters, and multiple datasets

# rename output files for afni
# rename new averaged variable names
# combine datasets

args <- commandArgs(trailingOnly = TRUE)
data_fname = args[1]
clin_fname = args[2]
target = args[3]
export_fname = args[4]
myseed = as.numeric(args[5])
min_cluster = args[6]

# starting h2o
library(h2o)
if (Sys.info()['sysname'] == 'Darwin') {
  max_mem = '16G'
  base_name = '~/data/'
} else {
  max_mem = paste(Sys.getenv('SLURM_MEM_PER_NODE'),'m',sep='')
  base_name = '/data/NCR_SBRB/'
}
h2o.init(ip='localhost', nthreads=future::availableCores(),
         max_mem_size=max_mem,
         port=sample(50000:60000, 1))  # jobs on same node use different ports

print('Loading files')
# merging phenotype and clinical data
clin = read.csv(clin_fname)

fnames = strsplit(data_fname, ',')
min_clusters = strsplit(min_cluster, ',')
for (f in 1:length(fnames[[1]])) {
    print(sprintf('Working with %s', fnames[[1]][f]))
    load(fnames[[1]][f])  #variable is data
    x_orig = colnames(data)[grepl(pattern = '^v', colnames(data))]
    # remove constant variables that screw up PCA and univariate tests
    print('Removing constant variables')
    feat_var = apply(data, 2, var, na.rm=TRUE)
    idx_var = feat_var != 0  # TRUE for features with 0 variance (constant)
    # categorical variables give NA variance, but we want to keep them
    idx_var[is.na(idx_var)] = TRUE
    data = data[, idx_var]
    nNAs = colSums(is.na(data))  # number of NAs in each variable
    # remove variables that are all NAs
    data = data[, nNAs < nrow(data)]
    print(sprintf('Features remaining: %d (%d with NAs)', ncol(data)-1, sum(nNAs>0)))
    print('Merging files')
    df = merge(clin, data, by='MRN')
    print('Looking for data columns')
    x = colnames(df)[grepl(pattern = '^v', colnames(df))]

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
            new_target = 'diag_group2'
        }
        if (group1 == 'rem' || group2 == 'rem') {
            keep_me = keep_me | df$diag_group2 == 2
            new_target = 'diag_group2'
        }
        if (group1 == 'imp' || group2 == 'imp') {
            keep_me = keep_me | df$groupSlope == 'improvers'
            new_target = 'groupSlope'
        }
        if (group1 == 'nonimp' || group2 == 'nonimp') {
            keep_me = keep_me | df$groupSlope == 'nonimprovers'
            new_target = 'groupSlope'
        }
        if (group1 == 'adhd' || group2 == 'adhd') {
            df[df$diag_group2 == 3, 'diag_group2'] = 2
            keep_me = keep_me | df$diag_group2 == 2
            new_target = 'diag_group2'
        }
        # remove NVs if we are doing imp vs nonImp
        if (sum(keep_me) == nrow(df) && (grepl('imp', group1) || grepl('imp', group2))) {
            df = df[df$diag_group2 != 1, ]
        } else {
            df = df[keep_me, ]
        }
        df[, new_target] = as.factor(as.character(df[, new_target]))
        print(table(df[, new_target]))
    }

    # set seed again to replicate old results
    library(caret)
    set.seed(myseed)
    train_idx = sort(createDataPartition(df[, new_target], p = .9, list = FALSE, times = 1))
    test_idx = sort(setdiff(1:nrow(df), train_idx)) # H2o only deals with sorted indexes
    data.test = df[test_idx, ]
    data.train = df[train_idx, ]
    print(sprintf('Using %d samples for training + validation, %d for testing.',
                nrow(data.train),
                nrow(data.test)))

    print('Running univariate analysis')
    data.train[, new_target] = as.factor(data.train[, new_target])
    b = sapply(data.train[, x],
                function(myx) {
                    res = kruskal.test(myx, data.train[, new_target]);
                    return(res$p.value)
                })
    keep_me = b <= .05
    print(sprintf('Variables before univariate filter: %d', length(x)))
    print(sprintf('Variables after univariate filter: %d', sum(keep_me)))

    # further filter variables to keep only the ones clustered together
    if (grepl(pattern='dti', fnames[[1]][f])) {
        ijk_fname = sprintf('%s/baseline_prediction/dti_223_ijk.txt', base_name)
        out_dir = sprintf('%s/tmp/', base_name)
        mask_fname = sprintf('%s/baseline_prediction/mean_223_fa_skeleton_mask.nii.gz',
                            base_name)
        out = read.table(ijk_fname)
        out[, 4] = 0
        out[keep_me, 4] = 1
        out_fname = sprintf('%s/%s_%d', out_dir, new_target, myseed)
        # writing good voxels to be clustered
        write.table(out, file=sprintf('%s.txt', out_fname), row.names=F, col.names=F)
        cmd_line = sprintf('cat %s.txt | 3dUndump -master %s -ijk -datum float -prefix %s -overwrite -;',
                            out_fname, mask_fname, out_fname)
        system(cmd_line)
        # spit out all clusters >= min_cluster
        cmd_line = sprintf('3dclust -NN1 %s -orient LPI -overwrite -savemask %s_mask %s+orig 2>/dev/null',
                            min_clusters[[1]][f], out_fname, out_fname)
        system(cmd_line)
        # read mask back in and filter x properly
        cmd_line = sprintf('3dmaskdump -mask %s %s_mask+orig > %s_mask.txt', mask_fname, out_fname, out_fname)
        system(cmd_line)
        clus = read.table(sprintf('%s_mask.txt', out_fname))
        cluster_idx = clus[, 4] > 0
        print(sprintf('Variables after spatial filter: %d', sum(cluster_idx)))
        # let's average within each cluster, and only keep those variables as good
        my_clusters = unique(clus[cluster_idx, 4])
        new_x = c()
        for (cl in 1:length(my_clusters)) {
            cluster_vars = clus[, 4] == my_clusters[cl]
            cl_avg = rowMeans(data.train[, x[cluster_vars]])
            data.train = cbind(data.train, cl_avg)
            colnames(data.train)[ncol(data.train)] = sprintf('v_ds%dclAvg%03d', f, cl)
            cl_avg = rowMeans(data.test[, x[cluster_vars]])
            data.test = cbind(data.test, cl_avg)
            colnames(data.test)[ncol(data.test)] = sprintf('v_ds%dclAvg%03d', f, cl)
            new_x = c(new_x, sprintf('v_ds%dclAvg%03d', f, cl))
        }
        # disregard all other variables and keep only the cluster averages
        x = new_x
    } else if (grepl(pattern='struct', fnames[[1]][f])) {
        # structural is a bit more challenging because left and right are separate
        nvox = length(x_orig)
        out_dir = sprintf('%s/tmp/', base_name)
        out = rep(0, nvox)
        names(out) = x_orig
        out[x[keep_me]] = 1
        out_fname = sprintf('%s/lh_%s_ds%d_%d', out_dir, new_target, f, myseed)

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
        out_fname = sprintf('%s/rh_%s_ds%d_%d', out_dir, new_target, f, myseed)

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
    } else {
        x = x[keep_me]
    }
    print(sprintf('Variables after spatial averaging: %d', length(x)))
    if (f > 1) {
        all_data.train = merge(all_data.train, data.train[, c('MRN', new_target, x)], by='MRN', all.x=T, all.y=T)
        all_data.test = merge(all_data.test, data.test[, c('MRN', new_target, x)], by='MRN', all.x=T, all.y=T)
        all_x = c(all_x, x)
        # combining targets
        cur_outcome = all_data.train[, paste0(new_target, '.x')]
        next_outcome = all_data.train[, paste0(new_target, '.y')]
        if ((sum(is.na(cur_outcome))==0) && (sum(is.na(next_outcome))==0) &&
             all(cur_outcome == next_outcome)) {
                # if the subjects are the same in both datasets, we're good
                all_data.train[, new_target] = all_data.train[, paste0(new_target, '.x')]
                all_data.test[, new_target] = all_data.test[, paste0(new_target, '.x')]
        } else {
            # if subjects are different, than they're NA in one of them. So,
            # copy the nonNas from the other
            outcome = all_data.train[, paste0(new_target, '.x')] # just for length
            new_scans = which(is.na(all_data.train[, paste0(new_target, '.x')]))
            outcome[new_scans] = all_data.train[new_scans, paste0(new_target, '.y')]
            new_scans = which(is.na(all_data.train[, paste0(new_target, '.y')]))
            outcome[new_scans] = all_data.train[new_scans, paste0(new_target, '.x')]
            all_data.train[, new_target] = outcome
            # and repeat the same for test
            outcome = all_data.test[, paste0(new_target, '.x')] # just for length
            new_scans = which(is.na(all_data.test[, paste0(new_target, '.x')]))
            outcome[new_scans] = all_data.test[new_scans, paste0(new_target, '.y')]
            new_scans = which(is.na(all_data.test[, paste0(new_target, '.y')]))
            outcome[new_scans] = all_data.test[new_scans, paste0(new_target, '.x')]
            all_data.test[, new_target] = outcome
        }
        all_data.train[, paste0(new_target, '.x')] = NULL
        all_data.train[, paste0(new_target, '.y')] = NULL
        all_data.test[, paste0(new_target, '.x')] = NULL
        all_data.test[, paste0(new_target, '.y')] = NULL
    } else {
        all_data.train = data.train[, c('MRN', new_target, x)]
        all_data.test = data.test[, c('MRN', new_target, x)]
        all_x = x
    }
}

print(sprintf('Final number of variables: %d', length(all_x)))
print('Converting to H2O')
dtrain = as.h2o(all_data.train[, c(all_x, new_target)])
dtest = as.h2o(all_data.test[, c(all_x, new_target)])
if (grepl(pattern = 'group', target)) {
    outcome = as.factor(as.h2o(df[, new_target]))  # making sure we have correct levels
    dtrain[, target] = outcome[train_idx]
    dtest[, target] = outcome[test_idx]
}

# make sure the SNPs are seen as factors
if (grepl(pattern = 'snp', data_fname)) {
  print('Converting SNPs to categorical variables')
  for (v in x) {
    dtrain[, v] = as.factor(dtrain[, v])
    dtest[, v] = as.factor(dtest[, v])
  }
}

# make sure some of the socioeconomic variables are seen as factors
if (grepl(pattern = 'social', data_fname)) {
  print('Converting some socioeconomics to categorical variables')
  for (v in c('v_CategCounty', 'v_CategHomeType')) {
      if (v %in% x) {
          dtrain[, v] = as.factor(dtrain[, v])
          dtest[, v] = as.factor(dtest[, v])
      }
  }
}

# use all binary clinic variables, regardless of univariate results
if (grepl(pattern = 'clinic', data_fname)) {
  print('Converting binary clinical variables')
  x = colnames(df)[grepl(pattern = '^v', colnames(df))]
  xbin = colnames(df)[grepl(pattern = '^vCateg', colnames(df))]
  for (v in xbin) {
    dtrain[, v] = as.factor(dtrain[, v])
    dtest[, v] = as.factor(dtest[, v])
  }
}

# use all adhd200 variables, regardless of univariate results
if (grepl(pattern = 'adhd', data_fname)) {
  print('Converting categorical variables')
  x = colnames(df)[grepl(pattern = '^v', colnames(df))]
  xbin = colnames(df)[grepl(pattern = '^vCateg', colnames(df))]
  for (v in xbin) {
    dtrain[, v] = as.factor(dtrain[, v])
    dtest[, v] = as.factor(dtest[, v])
  }
}

print(sprintf('Running model on %d features', length(all_x)))
aml <- h2o.automl(x = all_x, y = new_target, training_frame = dtrain,
                seed=myseed,
                leaderboard_frame=dtest,
                max_runtime_secs = NULL,
                max_models = NULL,
                exclude_algos = c("GBM", "GLM", "DRF", "StackedEnsemble"))

print(aml@leaderboard)

# dummy classifier
print('Class distribution:')
print(as.vector(h2o.table(dtrain[,new_target])['Count'])/nrow(dtrain))

print(data_fname)
print(clin_fname)
print(target)

# print test set ids
print('Test idx:')
print(test_idx)

# print predictions
print('Test set predictions:')
preds = h2o.predict(aml@leader, newdata=dtest[, all_x])
print(preds, n=nrow(preds))

# print all model metrics on test data
print(h2o.make_metrics(preds[,3], dtest[, new_target]))

# last thing is saving model, in case there are any permissions or I/O errors
h2o.saveModel(aml@leader, path = export_fname)