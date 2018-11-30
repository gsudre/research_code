# generates text files with results from univariate tests on randomized labels,
# to be later used to assess biggest cluster

args <- commandArgs(trailingOnly = TRUE)
data_fname = args[1]
clin_fname = args[2]
target = args[3]
myseed = as.numeric(args[4])
preproc = args[5]

# data_fname = '~/data/baseline_prediction/struct_area_11142018_260timeDiff12mo.RData.gz'
# clin_fname = '~/data/baseline_prediction/long_clin_11302018.csv'
# target = 'SX_inatt_baseline'
# myseed = 1234
# preproc = 'None'

winsorize = function(x, cut = 0.01){
  cut_point_top <- quantile(x, 1 - cut, na.rm = T)
  cut_point_bottom <- quantile(x, cut, na.rm = T)
  i = which(x >= cut_point_top) 
  x[i] = cut_point_top
  j = which(x <= cut_point_bottom) 
  x[j] = cut_point_bottom
  return(x)
}

if (Sys.info()['sysname'] == 'Darwin') {
  max_mem = '16G'
  base_name = '~/data/'
} else {
  max_mem = paste(Sys.getenv('SLURM_MEM_PER_NODE'),'m',sep='')
  base_name = '/data/NCR_SBRB/'
}
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
qc = read.csv(sprintf('%s/baseline_prediction/master_qc.csv', base_name))
df = merge(df, qc, by.x='mask.id', by.y='Mask.ID')
library(gdata)
mprage = read.xls(sprintf('%s/baseline_prediction/long_scans_08072018.xlsx', base_name),
                  sheet='mprage')
df = merge(df, mprage, by.x='mask.id', by.y='Mask.ID...Scan')

# checking for subgroup analysis. Options are nonew_OLS_*_slope, nonew_diag_group2,
# ADHDonly_OLS_*_slope, ADHDonly_diag_group2, nonew_ADHDonly_*, ADHDNOS_OLS_*_slope,
# ADHDNOS_groupOLS_*_slope, nonew_ADHDNOS_*
# for pairwise, we can do the usual nvVSper, nvVSrem, perVSrem, then
# groupOLS_SX_slope_ plus nvVSimp, nvVSnonimp, impVSnonimp, plus all of them
# using nonew_
input_target = target
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

# shuffling labels around if needed
if (myseed > 0) {
    idx = 1:nrow(df)
    suffix = ''
} else {
    myseed = -myseed
    set.seed(myseed)
    idx = sample(1:nrow(df), nrow(df), replace=F)
    suffix = 'rnd_'
}
df[, target] = df[idx, target]

if (grepl(pattern='subjScale', preproc)) {
    print('Normalizing within subjects')
    df[, x] = t(scale(t(df[, x])))
}

if (grepl(pattern='winsorize', preproc)) {
    print('Winsorizing target')
    df[, target] = winsorize(df[, target])
}

# first, generate main result
ps = vector()
ts = vector()
bs = vector()
set.seed(myseed)
library(nlme)
for (v in x) {
    # print(v)
    mydata = df[, c(target, 'Sex...Subjects', 'ext_avg_freesurfer5.3',
                    'int_avg_freesurfer5.3', 'mprage_QC',
                    'age_at_scan', 'nuclearFamID')]
    if (grepl(pattern='log', preproc)) {
        # make sure we have no negative values or zeros
        mydata$y = log(2*abs(min(df[,v])) + df[,v])
    } else {
        mydata$y = df[,v]
    }
    fm = as.formula(sprintf("y ~ %s + Sex...Subjects + ext_avg_freesurfer5.3 + int_avg_freesurfer5.3 + mprage_QC + age_at_scan + I(age_at_scan^2)", target))
    fit = try(lme(fm, random=~1|nuclearFamID, data=mydata, na.action=na.omit))
    if (length(fit) > 1) {
        ps = c(ps, summary(fit)$tTable[2,5])
        ts = c(ts, summary(fit)$tTable[2,4])
        bs = c(bs, summary(fit)$tTable[2,1])
    } else {
        ps = c(ps, 1)
        ts = c(ts, 0)
        bs = c(bs, 0)
    }
}

# write 1-p images and do clustering... attention to LH and RH!
junk = strsplit(data_fname, '/')[[1]]
pheno = strsplit(junk[length(junk)], '\\.')[[1]][1]
out_dir = sprintf('%s/tmp/%s/', base_name, pheno)
out_fname = sprintf('%s/%s_%s_%s%d', out_dir, input_target, preproc, suffix, myseed)

system(sprintf('mkdir %s', out_dir))
save(ps, ts, bs, file=sprintf('%s.RData', out_fname))

nvox = length(x_orig)  # before removing constant voxels!
out = rep(0, nvox)
names(out) = x_orig
keep_me = ps < .05
out[x[keep_me]] = 1

# writing good voxels to be clustered. left hemisphere first
write.table(out[1:(nvox/2)], file=sprintf('%s.txt', out_fname), row.names=F, col.names=F)

# spit out all clusters >= min_cluster
min_cluster = 1
cmd_line = sprintf('SurfClust -i %s/freesurfer5.3_subjects/fsaverage4/SUMA/lh.pial.asc -input %s.txt 0 -rmm -1.000000 -thresh_col 0 -athresh .95 -sort_area -no_cent -prefix %s_lh -out_roidset -out_fulllist -amm2 %d',
    base_name, out_fname, out_fname, min_cluster)
system(cmd_line)

# now, repeat the exact same thing for right hemisphere
write.table(out[(nvox/2+1):length(out)], file=sprintf('%s.txt', out_fname), row.names=F, col.names=F)
cmd_line = sprintf('SurfClust -i %s/freesurfer5.3_subjects/fsaverage4/SUMA/rh.pial.asc -input %s.txt 0 -rmm -1.000000 -thresh_col 0 -athresh .95 -sort_area -no_cent -prefix %s_rh -out_roidset -out_fulllist -amm2 %d',
    base_name, out_fname, out_fname, min_cluster)
system(cmd_line)
