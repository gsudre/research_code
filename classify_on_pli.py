"""

Classifies between ADHD and NV based on pli

"""
# Authors: Gustavo Sudre, 01/2013

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
from scipy import stats
import env

execfile('/Users/sudregp/research_code/combine_good_plis.py')

nv = nv.reshape([nv.shape[0], -1])
adhd = nv.reshape([adhd.shape[0], -1])
data = np.concatenate([nv, adhd], axis=0)
labels = np.ones([data.shape[0]])
labels[adhd.shape[0]:] = -1

data = stats.mstats.zscore(data, axis=0)

# removing any features with NaNs
data = data[:, ~np.isnan(data).any(0)]

loo = cross_validation.LeaveOneOut(len(labels))
clf = RandomForestClassifier(n_estimators=10, max_features=np.sqrt(data.shape[1]), max_depth=None, min_samples_split=1)
scores = []
for r in range(0):
    s = cross_validation.cross_val_score(clf, data, labels, cv=loo)
    scores.append(s.mean())
print 'Accuracy in LOOCV: ' + str(np.mean(scores)) + ' +- ' + str(np.std(scores))

clf = clf.fit(data, labels)
tmp = clf.predict(data)
print 'Accuracy in training: ' + str(np.sum(tmp == labels)/float(len(labels)))
