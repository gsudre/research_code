# generates text files with results from univariate tests on randomized labels,
# to be later used to assess biggest cluster

args <- commandArgs(trailingOnly = TRUE)
data_fname = args[1]
clin_fname = args[2]
target = args[3]
myseed = as.numeric(args[4])
preproc = args[5]

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
library(nlme)
library(MASS)
print(length(x))
for (v in x) {
    mydata = df[, c(target, 'Sex...Subjects', 'enormGoodTRs_fmri01', 'age_at_scan', 'nuclearFamID')]
    mydata$y = df[,v]
    fm = as.formula("y ~ Sex...Subjects + enormGoodTRs_fmri01 + I(enormGoodTRs_fmri01^2) + age_at_scan + I(age_at_scan^2)")
    fit = try(lme(fm, random=~1|nuclearFamID, data=mydata, na.action=na.omit, method='ML'))
    if (length(fit) > 1) {
        step = try(stepAIC(fit, direction = "both", trace = F))
        if (length(step) > 1) {
            mydata$y = residuals(step)
        } else {
            mydata$y = residuals(fit)
        }
        fm_str = sprintf('y ~ %s', target)
        fit = aov(lm(as.formula(fm_str), data=mydata))
        ps = c(ps, summary(fit)[[1]][1, 'Pr(>F)'])
    } else {
        ps = c(ps, 1)
    }
}

# write 1-p images and do clustering
if (grepl(pattern='fancy', data_fname)) {
    mask_fname = sprintf('%s/baseline_prediction/group_epi_mask_fancy.nii',
                        base_name)
    ijk_fname = sprintf('%s/baseline_prediction/melodic_fancy_ijk.txt', base_name)
} else if (grepl(pattern='union', data_fname)) {
    mask_fname = sprintf('%s/baseline_prediction/group_epi_mask_union.nii',
                        base_name)
    ijk_fname = sprintf('%s/baseline_prediction/melodic_union_ijk.txt', base_name)
} else {
    mask_fname = sprintf('%s/baseline_prediction/group_epi_mask_inter.nii',
                        base_name)
    ijk_fname = sprintf('%s/baseline_prediction/melodic_inter_ijk.txt', base_name)
}
out = read.table(ijk_fname)
out[, 4] = 0
keep_me = ps < .05
out[keep_me, 4] = 1

junk = strsplit(data_fname, '/')[[1]]
pheno = strsplit(junk[length(junk)], '\\.')[[1]][1]
out_dir = sprintf('%s/tmp/%s/', base_name, pheno)
system(sprintf('mkdir %s', out_dir))
out_fname = sprintf('%s/%s_%s_%s%d', out_dir, target, preproc, suffix, myseed)
save(ps, ts, bs, file=sprintf('%s.RData', out_fname))
# writing good voxels to be clustered
write.table(out, file=sprintf('%s.txt', out_fname), row.names=F, col.names=F)
cmd_line = sprintf('cat %s.txt | 3dUndump -master %s -ijk -datum float -prefix %s -overwrite -;',
                    out_fname, mask_fname, out_fname)
system(cmd_line)
# spit out all clusters
cmd_line = sprintf('3dclust -NN1 1 -orient LPI %s+tlrc 2>/dev/null > %s_clusters.txt',
                    out_fname, out_fname, out_fname)
system(cmd_line)