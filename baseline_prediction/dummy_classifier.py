from sklearn.model_selection import train_test_split
from sklearn.dummy import DummyClassifier
import pandas as pd
import numpy as np
import sys
import os
from sklearn.metrics import roc_auc_score


home = os.path.expanduser('~')

phen_fname = sys.argv[1]
target = sys.argv[2]
features_fname = sys.argv[3]
output_dir = sys.argv[4]
myseed = int(sys.argv[5])

phen_fname = home + '/data/baseline_prediction/dti_JHUtracts_ADRDonly_OD0.95.csv'
target = 'SX_HI_groupStudy'
features_fname = home + '/data/baseline_prediction/ad_rd_vars.txt'
output_dir = home + '/data/tmp/'
myseed = 42

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
X = data[feature_names].values

clf = DummyClassifier(strategy='most_frequent', random_state=myseed)
clf.fit(X[training_indices], target_class[training_indices])
preds = clf.predict(X[validation_indices])
score_majority = roc_auc_score(data.loc[validation_indices, 'class'].values,
                               preds)
                           
clf = DummyClassifier(strategy='stratified', random_state=myseed)
clf.fit(X[training_indices], target_class[training_indices])
preds = clf.predict(X[validation_indices])
score_strat = roc_auc_score(data.loc[validation_indices, 'class'].values,
                               preds)


out_fname = '%s_%s_%d' % (phen_fname.split('/')[-1].replace('.csv', ''),
                            target, myseed)
fout = open('%s/classification_dummy_results.csv' % output_dir, 'a')
fout.write('%s,%f,%f\n' % (out_fname, score_majority, score_strat))
fout.close()
