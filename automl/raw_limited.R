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
h2o.init(ip='localhost', nthreads=future::availableCores(), max_mem_size=paste(Sys.getenv('SLURM_MEM_PER_NODE'),'m',sep=''))

# merging phenotype and clinical data
clin = h2o.importFile(clin_fname)
data = h2o.importFile(data_fname)
print('Done loading files')
df = h2o.merge(clin, data, by='mask.id')
print('Done merging files')

# identify voxels
x = colnames(df)[grepl(pattern = '^v', colnames(df))]

# winsorize if it's a continuous variable
if (! grepl(pattern = 'group', target)) {
  df[, target] = winsorize(df[, target])
}

# groups need to be factors, after the h2o dataframe is created!
if (grepl(pattern = 'group', target)) {
  df[, target] = as.factor(df[, target])
}

print(sprintf('Running model on %d features', ncol(df)-1))

aml <- h2o.automl(x = x, y = target, training_frame = df,
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
