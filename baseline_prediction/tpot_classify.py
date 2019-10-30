from tpot import TPOTClassifier, config
from sklearn.model_selection import train_test_split
import pandas as pd
import numpy as np
from dask.distributed import Client
import sys
import os

ncpus = int(os.environ.get('SLURM_CPUS_PER_TASK', '2'))

client = Client(n_workers=ncpus, threads_per_worker=1)

phen_fname = sys.argv[1]
target = sys.argv[2]
features_fname = sys.argv[3]
output_dir = sys.argv[4]
myseed = int(sys.argv[5])

data = pd.read_csv(phen_fname)
data.rename(columns={target: 'class'}, inplace=True)
data['class'] = data['class'].map({'improvers': 1, 'nonimprovers': -1})
print(data['class'].value_counts())

fid = open(features_fname, 'r')
feature_names = [line.rstrip() for line in fid]
fid.close()

target_class = data['class'].values
training_indices, validation_indices = train_test_split(data.index,
														stratify = target_class, train_size=0.75,
														test_size=0.25,
														random_state=myseed)

# removing some warnings by hard coding parameters in the dictionary
my_config = config.classifier_config_dict
my_config['sklearn.linear_model.LogisticRegression']['solver'] = 'lbfgs'
preproc = [v for v in my_config.keys() if v.find('preprocessing') > 0]
for p in preproc:
	my_config[p]['validate'] = [False]

tpot = TPOTClassifier(n_jobs=-1, random_state=myseed, verbosity=2,
						config_dict=my_config, use_dask=True, scoring='roc_auc')

X = data[feature_names].values
tpot.fit(X[training_indices], target_class[training_indices])

### after
out_fname = '%s_%s_%d'
tpot.export('%s/%s_tpot_pipeline.py' % (output_dir, out_fname))

val_score = tpot.score(X[validation_indices],
                       data.loc[validation_indices, 'class'].values)

fout = open('%s/results.csv' % output_dir, 'a')
fout.write('%s,%f\n' % (out_fname, val_score))
