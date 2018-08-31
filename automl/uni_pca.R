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
h2o.init(ip='localhost', nthreads=future::availableCores(), max_mem_size='30G')

# merging phenotype and clinical data
clin = h2o.importFile(clin_fname)
data = h2o.importFile(data_fname)
df = h2o.merge(clin, data, by='mask.id')

# identify voxels and run PCA
x = colnames(df)[grepl(pattern = '^v', colnames(df))]

a = cbind(as.matrix(df[, x]), as.vector(df[, target]))
colnames(a)[ncol(a)] = target

# winsorize and get univariates if it's a continuous variable
if (! grepl(pattern = 'group', target)) {
  b = sapply(as.data.frame(a[,x]),
             function(myx) {
               res = cor.test(myx, a[, target], method='spearman');
               return(res$p.value)
             })
  # winsorizing after correlations to avoid ties
  a[, target] = winsorize(a[, target])
} else {
  a[, target] = as.factor(a[, target])
  b = sapply(as.data.frame(a[,x]),
             function(myx) {
               res = kruskal.test(myx, a[, target]);
               return(res$p.value)
             })
}
keep_me = b <= .05
a = a[, keep_me]

print(dim(a))

x = colnames(a)[grepl(pattern = '^v', colnames(a))]
pca = prcomp(a[, x], scale=T)
eigs <- pca$sdev^2
vexp = cumsum(eigs)/sum(eigs)
keep_me = vexp <= .95
a = cbind(pca$x[, keep_me], as.vector(df[, target]))
colnames(a)[ncol(a)] = target
x = colnames(a)[grepl(pattern = '^PC', colnames(a))]

# transform it back to h2o data frame
df2 = as.h2o(a)
# groups need to be factors, after the h2o dataframe is created!
if (grepl(pattern = 'group', target)) {
  df2[, target] = as.factor(df2[, target])
}

x = colnames(df2)[grepl(pattern = '^PC', colnames(df2))]
aml <- h2o.automl(x = x, y = target, training_frame = df2,
                  seed=42,
                  max_runtime_secs = NULL,
                  max_models = NULL)

print(data_fname)
print(clin_fname)
print(target)
print(dim(df2))
print(aml@leaderboard)
h2o.saveModel(aml@leader, path = export_fname)
