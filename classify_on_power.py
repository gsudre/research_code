"""

Classifies between ADHD and NV based on band power

"""
# Authors: Gustavo Sudre, 01/2013

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
from scipy import stats
import env

res = env.load(env.results + 'roi_power_chl.5_lp58_hp.5_th3500e15.npz')

subjs = list(res['good_nvs']) + list(res['good_adhds'])
num_roi = 68
num_band = 5

band_psd = np.empty([len(subjs), num_roi * num_band])
labels = np.empty([len(subjs)])
rm = []
for s, subj in enumerate(subjs):
    subj_data = res['power'][subj].ravel()
    if not any(np.isnan(subj_data)):
        band_psd[s, :] = subj_data
        if any(subj in i for i in res['good_adhds']):
            labels[s] = -1
        else:
            labels[s] = 1
    else:
        rm.append(s)
band_psd = np.delete(band_psd, rm, axis=0)
labels = np.delete(labels, rm, axis=0)

band_psd = stats.mstats.zscore(band_psd, axis=0)

loo = cross_validation.LeaveOneOut(len(labels))
clf = RandomForestClassifier(n_estimators=100, max_features=19, max_depth=None, min_samples_split=1)
scores = []
for r in range(10):
    s = cross_validation.cross_val_score(clf, band_psd, labels, cv=loo)
    scores.append(s.mean())
print 'Accuracy in LOOCV: ' + str(np.mean(scores)) + ' +- ' + str(np.std(scores))

clf = clf.fit(band_psd, labels)
tmp = clf.predict(band_psd)
print 'Accuracy in training: ' + str(np.sum(tmp == labels)/float(len(labels))

