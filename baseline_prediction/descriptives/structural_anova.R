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

# creating the categories based on OLS SX
df$OLS_inatt_categ = NULL
df[df$OLS_inatt_slope <= -.33, 'OLS_inatt_categ'] = 'marked'
df[df$OLS_inatt_slope > -.33 & df$OLS_inatt_slope <= 0, 'OLS_inatt_categ'] = 'mild'
df[df$OLS_inatt_slope > 0, 'OLS_inatt_categ'] = 'deter'
df[df$DX == 'NV', 'OLS_inatt_categ'] = 'NV'
df$OLS_inatt_categ = as.factor(df$OLS_inatt_categ)
df$OLS_inatt_categ = relevel(df$OLS_inatt_categ, ref='NV')
df$OLS_HI_categ = NULL
df[df$OLS_HI_slope <= -.5, 'OLS_HI_categ'] = 'marked'
df[df$OLS_HI_slope > -.5 & df$OLS_HI_slope <= 0, 'OLS_HI_categ'] = 'mild'
df[df$OLS_HI_slope > 0, 'OLS_HI_categ'] = 'deter'
df[df$DX == 'NV', 'OLS_HI_categ'] = 'NV'
df$OLS_HI_categ = as.factor(df$OLS_HI_categ)
df$OLS_HI_categ = relevel(df$OLS_HI_categ, ref='NV')

for (t in c('age_at_scan', 'I(age_at_scan^2)', 'ext_avg_freesurfer5.3', 'int_avg_freesurfer5.3', 'mprage_QC', 'as.numeric(Sex...Subjects)')) {
  fm_str = sprintf('%s ~ OLS_HI_categ', t)
  print(fm_str)
  print(summary(aov(lm(as.formula(fm_str), data=df))))
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

# first, generate main result
ps = vector()
ts = vector()
bs = vector()
set.seed(myseed)
for (v in x) {
    fm_str = sprintf('%s ~ %s', v, target)
    fit = aov(lm(as.formula(fm_str), data=df))
    if (length(fit) > 1) {
        ps = c(ps, summary(fit)[[1]][1, 'Pr(>F)'])
    } else {
        ps = c(ps, 1)
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
