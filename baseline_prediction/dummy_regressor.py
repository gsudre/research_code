from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyRegressor
import pandas as pd
import numpy as np
import sys
import os
from sklearn.metrics import mean_absolute_error


home = os.path.expanduser('~')

phen_fname = sys.argv[1]
target = sys.argv[2]
features_fname = sys.argv[3]
output_dir = sys.argv[4]
myseed = int(sys.argv[5])

data = pd.read_csv(phen_fname)
data.rename(columns={target: 'class'}, inplace=True)

fid = open(features_fname, 'r')
feature_names = [line.rstrip() for line in fid]
fid.close()

target_class = data['class'].values
training_indices, validation_indices = train_test_split(data.index,
                                                        train_size=0.8,
                                                        test_size=0.2,
                                                        random_state=myseed)

X = data[feature_names].values

clf = DummyRegressor(strategy='mean')
clf.fit(X[training_indices], target_class[training_indices])
preds = clf.predict(X[validation_indices])
score_mean = -1 * mean_absolute_error(target_class[validation_indices], preds)
                           
clf = DummyRegressor(strategy='median')
clf.fit(X[training_indices], target_class[training_indices])
preds = clf.predict(X[validation_indices])
score_median = -1 * mean_absolute_error(target_class[validation_indices], preds)

### after
phen = phen_fname.split('/')[-1].replace('.csv', '')
out_fname = '%s_%s_%d' % (phen, target, myseed)
fout = open('%s/regression_dummy_results_%s.csv' % (output_dir, phen), 'a')
fout.write('%s,%f,%f\n' % (out_fname, score_mean, score_median))
fout.close()
