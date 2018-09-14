# runs classification tasks using AutoML from H2O

args <- commandArgs(trailingOnly = TRUE)
data_fname = args[1]
clin_fname = args[2]
target = args[3]
export_fname = args[4]


winsorize = function(x, cut = 0.01){
  cut_point_top <- quantile(x, 1 - cut, na.rm = T)
  cut_point_bottom <- quantile(x, cut, na.rm = T)
  i = which(x >= cut_point_top) 
  x[i] = cut_point_top
  j = which(x <= cut_point_bottom) 
  x[j] = cut_point_bottom
  return(x)
}

# starting h2o
library(h2o)
if (Sys.info()['sysname'] == 'Darwin') {
  max_mem = '16G'
} else {
  max_mem = paste(Sys.getenv('SLURM_MEM_PER_NODE'),'m',sep='')
}
h2o.init(ip='localhost', nthreads=future::availableCores(), max_mem_size=max_mem)

print('Loading files')
# merging phenotype and clinical data
clin = read.csv(clin_fname)
load(data_fname)  #variable is data
# remove constant variables that screw up PCA and univariate tests
print('Removing constant variables and NAs')
keep_me = colSums(is.na(data)) == 0
data = data[, keep_me]
feat_var = apply(data, 2, var, na.rm=TRUE)
data = data[, feat_var != 0]
print('Merging files')
df = merge(clin, data, by='mask.id')
print('Looking for data columns')
x = colnames(df)[grepl(pattern = '^v', colnames(df))]

print('Running univariate analysis')
# winsorize and get univariates if it's a continuous variable
if (! grepl(pattern = 'group', target)) {
  b = sapply(df[,x],
             function(myx) {
               res = cor.test(myx, df[, target], method='spearman');
               return(res$p.value)
             })
  # winsorizing after correlations to avoid ties
  df[, target] = winsorize(df[, target])
} else {
  df[, target] = as.factor(df[, target])
  b = sapply(df[,x],
             function(myx) {
               res = kruskal.test(myx, df[, target]);
               return(res$p.value)
             })
}
keep_me = b <= .05
x = x[keep_me]

print('Converting to H2O')
df2 = as.h2o(df[, c(x, target)])
if (grepl(pattern = 'group', target)) {
  df2[, target] = as.factor(df2[, target])
}

print(sprintf('Running model on %d features', length(x)))
aml <- h2o.automl(x = x, y = target, training_frame = df2,
                  seed=42,
                  max_runtime_secs = 3600*24*2,
                  max_models = NULL,
                exclude_algos = c("GBM", "StackedEnsemble", "DRF"))

print(data_fname)
print(clin_fname)
print(target)
print(dim(df2))
print(aml@leaderboard)
h2o.saveModel(aml@leader, path = export_fname)
