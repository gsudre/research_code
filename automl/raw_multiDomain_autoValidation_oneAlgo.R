# runs classification tasks using AutoML from H2O. Using CV for scoring, raw features,
# multiple datasets

args <- commandArgs(trailingOnly = TRUE)
data_fname = args[1]
clin_fname = args[2]
target = args[3]
export_fname = args[4]
myseed = as.numeric(args[5])
algo = args[6]

if (myseed < 0) {
    randomize_data = T
    myseed = -1 * myseed
} else {
    randomize_data = F
}

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
    set.seed(myseed)
    print(sprintf('Using all %d samples for training + validation (CV results for leaderboard).',
                nrow(df)))
    
    if (f > 1) {
        all_data = merge(all_data, df[, c('MRN', new_target, x)], by='MRN', all.x=T, all.y=T)
        # combining targets
        cur_outcome = all_data[, paste0(new_target, '.x')]
        next_outcome = all_data[, paste0(new_target, '.y')]
        if ((sum(is.na(cur_outcome))==0) && (sum(is.na(next_outcome))==0) &&
             all(cur_outcome == next_outcome)) {
                # if the subjects are the same in both datasets, we're good
                all_data[, new_target] = all_data[, paste0(new_target, '.x')]
        } else {
            # if subjects are different, than they're NA in one of them. So,
            # copy the nonNas from the other
            outcome = all_data[, paste0(new_target, '.x')] # just for length
            new_scans = which(is.na(all_data[, paste0(new_target, '.x')]))
            outcome[new_scans] = all_data[new_scans, paste0(new_target, '.y')]
            new_scans = which(is.na(all_data[, paste0(new_target, '.y')]))
            outcome[new_scans] = all_data[new_scans, paste0(new_target, '.x')]
            all_data[, new_target] = outcome
        }
        all_data[, paste0(new_target, '.x')] = NULL
        all_data[, paste0(new_target, '.y')] = NULL
    } else {
        all_data = df[, c('MRN', new_target, x)]
    }
}
all_x = colnames(all_data)[grepl(pattern = '^v', colnames(all_data))]

print(sprintf('Final number of variables: %d', length(all_x)))

# use negative seed to randomize the data
if (randomize_data) {
  print('Creating random data!!!')
  set.seed(myseed)
  rnd_data = matrix(runif(nrow(all_data) * length(all_x),
                          min(all_data[, all_x], na.rm=T),
                          max(all_data[, all_x], na.rm=T)),
                    nrow(all_data), length(all_x))
  all_data[, all_x] = rnd_data
}

print('Converting to H2O')
dtrain = as.h2o(all_data[, c(all_x, new_target)])
if (grepl(pattern = 'group', target)) {
    outcome = as.factor(as.h2o(all_data[, new_target]))  # making sure we have correct levels
    dtrain[, target] = outcome
}

# make sure the SNPs are seen as factors
if (grepl(pattern = 'snp', data_fname)) {
  print('Converting SNPs to categorical variables')
  for (v in all_x) {
    dtrain[, v] = as.factor(dtrain[, v])
  }
}

# make sure some of the socioeconomic variables are seen as factors
if (grepl(pattern = 'social', data_fname)) {
  print('Converting some socioeconomics to categorical variables')
  for (v in c('v_CategCounty', 'v_CategHomeType')) {
      if (v %in% all_x) {
          dtrain[, v] = as.factor(dtrain[, v])
      }
  }
}

# use all binary clinic variables
if (grepl(pattern = 'clinic', data_fname)) {
  print('Converting binary clinical variables')
  xbin = colnames(dtrain)[grepl(pattern = '^vCateg', colnames(dtrain))]
  for (v in xbin) {
    dtrain[, v] = as.factor(dtrain[, v])
  }
}

# use all adhd200 variables
if (grepl(pattern = 'adhd', data_fname)) {
  print('Converting categorical variables')
  xbin = colnames(dtrain)[grepl(pattern = '^vCateg', colnames(dtrain))]
  for (v in xbin) {
    dtrain[, v] = as.factor(dtrain[, v])
  }
}

all_algos = c("DeepLearning", "GBM", "GLM", "DRF", "StackedEnsemble")
exclude_algos = setdiff(all_algos, algo)
print(sprintf('Running model on %d features', length(all_x)))
aml <- h2o.automl(x = all_x, y = new_target, training_frame = dtrain,
                seed=myseed,
                max_runtime_secs = NULL,
                max_models = NULL,
                exclude_algos = exclude_algos)

print(aml@leaderboard)

# dummy classifier
if (grepl(pattern = 'group', new_target)) {
    print('Class distribution:')
    print(as.vector(h2o.table(dtrain[,new_target])['Count'])/nrow(dtrain))
} else {
    preds = rep(mean(dtrain[,new_target]), nrow(dtrain))
    m = h2o.make_metrics(as.h2o(preds), dtrain[, new_target])
    print('MSE prediction mean:')
    print(m@metrics$MSE)
}

print(data_fname)
print(clin_fname)
print(target)

# print predictions
print('CV predictions:')
preds = h2o.getFrame(aml@leader@model[["cross_validation_holdout_predictions_frame_id"]][["name"]])
print(preds, n=nrow(preds))

# print all model metrics on CV data
print(aml@leader)

# last thing is saving model, in case there are any permissions or I/O errors
h2o.saveModel(aml@leader, path = export_fname)