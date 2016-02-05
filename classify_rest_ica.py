# classify MEG and fMRI ICA results combined

import os
import numpy as np
import pylab as pl
import nibabel as nb
home = os.path.expanduser('~')
import sys
import itertools
from sklearn import preprocessing, lda, svm
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
from sklearn.cross_validation import LeaveOneOut, StratifiedShuffleSplit

# NEXT:
# FIND BEST CLASSIFIER


def get_scores(X, y):
    nfolds = 40
    cv = StratifiedShuffleSplit(y, n_iter=nfolds, test_size=.05)
    dumb = DummyClassifier(strategy='most_frequent')
    clf = svm.SVC(class_weight='auto')
    param_dist = {"C": [.1, 1, 10],
                  "kernel": ['rbf', 'linear', 'poly']
                  }
    search = GridSearchCV(clf, param_grid=param_dist,
                          scoring='mean_absolute_error')
    stest, strain, sdummy = [], [], []
    for nfeats in range(X.shape[1]):
        test_scores, train_scores, dummy_scores = [], [], []
        # figure out our possible feature combinations
        feats = itertools.combinations(range(X.shape[1]), nfeats + 1)
        for my_feats in feats:
            for oidx, (train, test) in enumerate(cv):
                idx = np.array(my_feats)
                y_train, y_test = y[train], y[test]
                X_train, X_test = X[train, :], X[test, :]

                search.fit(X_train, y_train)
                clf = search.best_estimator_

                clf.fit(X_train[:, idx], y_train)
                train_scores.append(accuracy_score(clf.predict(X_train[:, idx]), y_train))
                test_scores.append(accuracy_score(clf.predict(X_test[:, idx]), y_test))
                dumb.fit(X_train[:, idx], y_train)
                dummy_scores.append(accuracy_score(dumb.predict(X_test[:, idx]), y_test))
        sdummy.append(np.mean(dummy_scores))
        strain.append(np.mean(train_scores))
        stest.append(np.mean(test_scores))
    return stest, strain, sdummy


phen = np.recfromcsv(home + '/data/overlap_resting/subjs.csv')
my_groups = ['NV', 'persistent', 'remission']

fdata_dir = home + '/data/fmri/ica/dual_regression_AllSubjsZeroFilled/'
fres_dir = home + '/data/fmri/ica/results_AllSubjsZeroFilled/'
fres_fname = ['clustmask_p95a90_anovaAgeGender_IC03.nii',
              'clustmask_p95a90_anovaAgeGender_IC15.nii',
              'clustmask_p95a90_anovaAgeGender_IC18.nii',
              'clustmask_p95a90_anovaAgeGender_IC22.nii']

mdata_dir = home + '/data/meg/ica/'
mres_dir = mdata_dir + 'results_correlation/'
mres_fname = ['clustmaskAllBands_p99a99Corr_anovaAgeGender_65-100_IC06.nii',
              'clustmaskAllBands_p99a99Corr_anovaAgeGender_65-100_IC04.nii',
              'clustmaskAllBands_p99a99Corr_anovaAgeGender_4-8_IC14.nii',
              'clustmaskAllBands_p99a99Corr_anovaAgeGender_4-8_IC06.nii']

sx = [rec[2] for rec in phen]
inatt = [rec[3] for rec in phen]
hi = [rec[4] for rec in phen]
total = [i + j for i, j in zip(inatt, hi)]

# # open fMRI data
# fmri = []  # list of data per cluster
# print 'Loading fMRI data'
# for res in fres_fname:
#     mask = nb.load(fres_dir + res)
#     cl_values = np.unique(mask.get_data())[1:]  # remove 0
#     nclusters = max(cl_values)
#     ic = res.split('IC')[-1][:2]
#     for c in range(nclusters):
#         cl_data = []
#         gv = mask.get_data() == cl_values[c]
#         for rec in phen:
#             fname = '%s/dr_stage2_%04d.nii.gz' % (fdata_dir, rec[0])
#             img = nb.load(fname)
#             subj_data = img.get_data()[gv, int(ic)]  # load beta coefficients
#             cl_data.append(float(np.nanmean(subj_data)))
#     fmri.append(cl_data)
# # makes fmri subjs x result
# fmri = np.array(fmri).T

# # open MEG data
# meg = []  # list of data per cluster
# print 'Loading MEG data'
# for res in mres_fname:
#     mask = nb.load(mres_dir + res)
#     cl_values = np.unique(mask.get_data())[1:]  # remove 0
#     nclusters = max(cl_values)
#     freq_band = res.split('_')[-2]
#     ic = res.split('IC')[-1][:2]
#     for c in range(nclusters):
#         cl_data = []
#         gv = mask.get_data() == cl_values[c]
#         for rec in phen:
#             fname = '%s/%s_%s_IC%s.nii' % (mdata_dir, rec[1], freq_band, ic)
#             img = nb.load(fname)
#             subj_data = img.get_data()[gv, 2]  # load correlation
#             cl_data.append(float(np.nanmean(subj_data)))
#         meg.append(cl_data)
# meg = np.array(meg).T

y = preprocessing.LabelEncoder().fit_transform(sx)
F = preprocessing.scale(fmri)
M = preprocessing.scale(meg)

from sklearn.metrics import accuracy_score
from sklearn.dummy import DummyClassifier
clf = lda.LDA()
from sklearn.decomposition import RandomizedPCA

mtest_scores, mtrain_scores, mdummy_scores = [], [], []


ftest, ftrain, fdumb = get_scores(F, y)
mtest, mtrain, mdumb = get_scores(M, y)
ncomp = max(F.shape[1], M.shape[1])
pca = RandomizedPCA(n_components=ncomp, whiten=True)
both = np.hstack([F, M])
btest, btrain, bdumb = get_scores(pca.fit_transform(both), y)

# plotting results
nfeats = np.arange(ncomp)
bar_width = .25
colors = ['r', 'g', 'b']
fig = pl.figure()
pl.subplot(1, 3, 1)
res = [fdumb, mdumb, bdumb]
for d in range(3):
    pl.bar(nfeats[:len(res[d])] + d * bar_width, res[d], bar_width,
           color=colors[d])
pl.ylim(0, 1)
pl.title('Dummy')
pl.legend(['fMRI', 'MEG', 'Combined'])
pl.subplot(1, 3, 2)
res = [ftrain, mtrain, btrain]
for d in range(3):
    pl.bar(nfeats[:len(res[d])] + d * bar_width, res[d], bar_width,
           color=colors[d])
pl.ylim(0, 1)
pl.title('Train')
pl.subplot(1, 3, 3)
res = [ftest, mtest, btest]
for d in range(3):
    pl.bar(nfeats[:len(res[d])] + d * bar_width, res[d], bar_width,
           color=colors[d])
pl.ylim(0, 1)
pl.title('Test')
