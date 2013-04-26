"""

Classifies between ADHD and NV based on band power

"""
# Authors: Gustavo Sudre, 01/2013

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn import cross_validation
from scipy import stats
import env
from sklearn.feature_selection import RFECV
from sklearn.svm import SVC
from sklearn.feature_selection import SelectPercentile, f_classif

res = env.load(env.results + 'roi_power_chl.5_lp58_hp.5_th3500e15.npz')

subjs = list(res['good_nvs']) + list(res['good_adhds'])
num_roi = 68
num_band = 5

labels = np.empty([len(subjs)])
for s, subj in enumerate(subjs):
    if any(subj in i for i in res['good_adhds']):
        labels[s] = -1
    else:
        labels[s] = 1

### BAND PSD FEATURES ###
band_psd = np.empty([len(subjs), num_roi * num_band])
band_psd[:] = np.NaN
for s, subj in enumerate(subjs):
    # res['power'][subj] is rois x bands
    subj_data = res['power'][subj].ravel()
    band_psd[s, :] = subj_data

### PCT OF WHOLE BRAIN POWER WITHIN BAND FEATURES ###
# it shows how important the power in each roi is within a band
pct_whole = np.empty([len(subjs), num_roi * num_band])
pct_whole[:] = np.NaN
for s, subj in enumerate(subjs):
    subj_pow = res['power'][subj]
    subj_data = np.divide(subj_pow, np.nansum(subj_pow, axis=0))
    pct_whole[s, :] = subj_data.ravel()

### PCT OF ALL POWER FEATURES ###
# for the power spectrum of the roi, how big is the chunk that band represents
pct_pow = np.empty([len(subjs), num_roi * num_band])
pct_pow[:] = np.NaN
for s, subj in enumerate(subjs):
    subj_pow = res['power'][subj]
    subj_data = np.divide(subj_pow.T, np.nansum(subj_pow, axis=1))
    pct_pow[s, :] = subj_data.ravel()

### PCT OF ALPHA FEATURES ###
# how big the power in a given ROIxband is with respect to the power in alpha (e.g. see Osipova's paper)
pct_alpha = np.empty([len(subjs), num_roi * (num_band - 1)])
pct_alpha[:] = np.NaN
for s, subj in enumerate(subjs):
    subj_pow = res['power'][subj]
    subj_data = np.divide(subj_pow.T, subj_pow[:, 2])
    subj_data = np.delete(subj_data, 2, axis=0)
    pct_alpha[s, :] = subj_data.ravel()

### THETHA TO GAMMA RATIO ###
# how big the power in ROIxtheta is with respect to the power in gamma (e.g. see paper with Becker)
pct_thetaXgamma = np.empty([len(subjs), num_roi])
pct_thetaXgamma[:] = np.NaN
for s, subj in enumerate(subjs):
    subj_pow = res['power'][subj]
    subj_data = np.divide(subj_pow[:, 1], subj_pow[:, 4])
    pct_thetaXgamma[s, :] = subj_data

#### DONE MAKING UP FEATURES #####

features = np.concatenate((band_psd, pct_whole, pct_pow, pct_alpha, pct_thetaXgamma), axis=1)

# removing any features with NaNs
good_features = ~np.isnan(features).any(0)
features = features[:, good_features]

features = stats.mstats.zscore(features, axis=0)

loo = cross_validation.LeaveOneOut(len(labels))
clf = RandomForestClassifier(n_estimators=500, max_features=np.sqrt(features.shape[1]), max_depth=None, min_samples_split=1, compute_importances=True)

# svc = SVC(kernel="linear")
# rfecv = RFECV(estimator=svc, step=.1, cv=loo)
# rfecv.fit(features, labels)

top_features = 50
# computing feature importance
acc = 0
cnt = .0
for train_index, test_index in loo:
    # feature_scores = np.zeros([features.shape[1]])
    # for r in range(10):
    #     clf = clf.fit(features[train_index, :], labels[train_index])
    #     feature_scores += clf.feature_importances_
    # indices = np.argsort(feature_scores)[::-1]

    selector = SelectPercentile(f_classif, percentile=10)
    selector.fit(features[train_index, :], labels[train_index])
    feature_scores = selector.scores_
    indices = np.argsort(feature_scores)[::-1]

    clf2 = RandomForestClassifier(n_estimators=500, max_features=np.sqrt(top_features), max_depth=None, min_samples_split=1)
    best_features = features[:, indices[:top_features]]

    for r in range(10):
        clf2 = clf2.fit(best_features[train_index, :], labels[train_index])
        acc += clf2.score(best_features[test_index, :], labels[test_index])
        print acc
        cnt += 1
acc /= cnt

# scores = []
# for r in range(2):

#     s = cross_validation.cross_val_score(clf, features, labels, cv=loo)
#     scores.append(s.mean())
# print 'Accuracy in LOOCV: ' + str(np.mean(scores)) + ' +- ' + str(np.std(scores))


# clf = clf.fit(features, labels)
# tmp = clf.predict(features)
# print 'Accuracy in training: ' + str(np.sum(tmp == labels)/float(len(labels)))
