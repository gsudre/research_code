# generates text files with results from univariate tests on randomized labels,
# to be later used to assess biggest cluster

args <- commandArgs(trailingOnly = TRUE)
data_fname = args[1]
clin_fname = args[2]
target = args[3]
myseed = as.numeric(args[4])
preproc = args[5]

# data_fname = '~/data/baseline_prediction/clinics_binary_sx_baseline_10022018.RData.gz'
# clin_fname = '~/data/baseline_prediction/long_clin_11302018.csv'
# target = 'ADHDNOS_nonew_OLS_inatt_slope'
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

# make sure the SNPs are seen as factors
if (grepl(pattern = 'snp', data_fname)) {
  print('Converting SNPs to categorical variables')
  xbin = colnames(df)[grepl(pattern = '^v_rs', colnames(df))]
  for (v in xbin) {
    df[, v] = as.factor(df[, v])
  }
}

# make sure some of the socioeconomic variables are seen as factors
if (grepl(pattern = 'social', data_fname)) {
  print('Converting some socioeconomics to categorical variables')
  for (v in c('v_CategCounty', 'v_CategHomeType')) {
      df[, v] = as.factor(df[, v])
  }
}

# use all binary clinic variables
if (grepl(pattern = 'clinic', data_fname)) {
  print('Converting binary clinical variables')
  xbin = colnames(df)[grepl(pattern = '^vCateg', colnames(df))]
  for (v in xbin) {
    df[, v] = as.factor(df[, v])
  }
}

# use all adhd200 variables
if (grepl(pattern = 'adhd', data_fname)) {
  print('Converting categorical variables')
  xbin = colnames(df)[grepl(pattern = '^vCateg', colnames(df))]
  for (v in xbin) {
    df[, v] = as.factor(df[, v])
  }
}

# first, generate main result
ps = vector()
ts = vector()
bs = vector()
set.seed(myseed)
library(nlme)
library(lme4)
good_vars = c()  # remove variables with singular computations from FDR and Meff
for (v in 1:length(x)) {
    # print(x[v])
    mydata = df[, c(target, 'nuclearFamID')]
    if (grepl(pattern='log', preproc)) {
        mydata$y = log(2*abs(min(df[, x[v]])) + df[, x[v]])
    } else {
        mydata$y = df[, x[v]]
    }
    if (is.factor(mydata$y)) {
        fm = as.formula(sprintf("y ~ %s + (1|nuclearFamID)", target))
        fit = try(glmer(fm, data=mydata, na.action=na.omit, family = binomial(link = "logit")))
        if (length(fit@optinfo$conv$lme4) > 0) {
            ps = c(ps, 1)
            ts = c(ts, 0)
            bs = c(bs, 0)
        } else {
            ps = c(ps, summary(fit)$coefficients[2,4])
            ts = c(ts, summary(fit)$coefficients[2,3])
            bs = c(bs, summary(fit)$coefficients[2,1])
            good_vars = c(good_vars, v)
        }
    } else {
        fm = as.formula(sprintf("y ~ %s", target))
        fit = try(lme(fm, random=~1|nuclearFamID, data=mydata, na.action=na.omit))
        if (length(fit) > 1) {
            ps = c(ps, summary(fit)$tTable[2,5])
            ts = c(ts, summary(fit)$tTable[2,4])
            bs = c(bs, summary(fit)$tTable[2,1])
            good_vars = c(good_vars, v)
        } else {
            ps = c(ps, 1)
            ts = c(ts, 0)
            bs = c(bs, 0)
        }
    }
}

print(sprintf('Keeping %d good variables out of %d', length(good_vars), length(ps)))
x = x[good_vars]
ps = ps[good_vars]
keep_me = ps < .05
junk = strsplit(data_fname, '/')[[1]]
pheno = strsplit(junk[length(junk)], '\\.')[[1]][1]
out_dir = sprintf('%s/tmp/%s/', base_name, pheno)
system(sprintf('mkdir %s', out_dir))
out_fname = sprintf('%s/%s_%s_%s%d', out_dir, input_target, preproc, suffix, myseed)
save(ps, ts, bs, file=sprintf('%s.RData', out_fname))

# spit out some stats
print(sprintf('Variables at p<.05: %d / %d', sum(keep_me), length(keep_me)))
print(x[keep_me])

ps2 = p.adjust(ps, method='fdr')
keep_me2 = ps2 < .05
print(sprintf('Variables at q<.05: %d / %d', sum(keep_me2), length(keep_me2)))
print(x[keep_me2])

# Using M(eff) from Galwey 2009
# Meff only applies to numeric variables!
use_me = c()
for (v in 1:length(x)) {
    if (is.numeric(df[, x[v]])) {
        use_me = c(use_me, v)
    }
}
numeric_df = df[, x[use_me]]
nNAs = rowSums(is.na(numeric_df))  # number of NAs in each subject
# remove subjects with at least one NA
# Meff is just an approximation, so losing a few subjects is not the end of the world
numeric_df = numeric_df[nNAs < 1, ]
# only run Meff is we have at least 3 variables (heuristic)
if (ncol(numeric_df) > 2) {
    cc = cor(numeric_df)
    svd = eigen(cc)
    absev = abs(svd$values)
    meff = (sum(sqrt(absev))^2)/sum(absev)
    print(sprintf('Galwey Meff = %.2f', meff))
    keep_me3 = ps[use_me] < (.05/meff)
    print(sprintf('Variables at q<Meff: %d / %d', sum(keep_me3), length(keep_me3)))
    print(x[keep_me3])
} else {
    print('Not enough numeric variables for Meff')
}