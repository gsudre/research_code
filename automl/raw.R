# runs classification tasks using AutoML from H2O

args <- commandArgs(trailingOnly = TRUE)
data_fname = args[1]
clin_fname = args[2]
target = args[3]
export_fname = args[4]
action = args[5]

library(h2o)
h2o.init(ip='localhost', nthreads=future::availableCores(), max_mem_size='30G')
clin = h2o.importFile(clin_fname)
data = h2o.importFile(data_fname)
df = h2o.merge(clin, data, by='mask.id')

x = colnames(df)[grepl(pattern = '^v', colnames(df))]
pca = prcomp(df[, x], scale=T)
a = cbind(pca$x, as.vector(df[, target]))
colnames(a)[264] = 
df2 = as.h2o(a)
df2[, target] = as.factor(df2[, y])
x = colnames(df2)[grepl(pattern = '^PC', colnames(df2))]

aml <- h2o.automl(x = x, y = target, training_frame = df2,
                  seed=42,
                  max_runtime_secs = NULL,
                  max_models = NULL)

print(aml@leaderboard)
h2o.saveModel(aml@leader, path = export_fname)
