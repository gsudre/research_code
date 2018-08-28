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

# we need to classify factors
if (action == 'c') {
  df[, target] = as.factor(df[, target])
}

x = colnames(df)[grepl(pattern = '^v', colnames(df))]

aml <- h2o.automl(x = x, y = target, training_frame = df,
                  seed=42,
                  max_runtime_secs = NULL,
                  max_models = NULL)

print(aml@leaderboard)
h2o.saveModel(aml@leader, path = export_fname)
