# classify MEG and fMRI ICA results combined

import os
import numpy as np
import pylab as pl
from scipy import stats
import nibabel as nb
home = os.path.expanduser('~')
import sys
import itertools
from sklearn import preprocessing, lda, svm, linear_model
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
from sklearn.cross_validation import LeaveOneOut, StratifiedShuffleSplit

# NEXT:
# FIND BEST CLASSIFIER


def get_scores(X, y):
    nfolds = 200
    cv = StratifiedShuffleSplit(y, n_iter=nfolds, test_size=.2)
    dumb = DummyClassifier(strategy='most_frequent')
    clf = svm.SVC(class_weight='auto')
    clf = linear_model.LogisticRegression()
    param_dist = {"C": [.1, 1, 10],
                  "kernel": ['rbf', 'linear', 'poly']
                  }
    param_dist = {"C": [1e6, 1e5, 1e4, 1e3, 1e2, 10, 1, .1, .01, .001]}
    search = GridSearchCV(clf, param_grid=param_dist,
                          scoring='mean_absolute_error')
    test_scores, train_scores, dummy_scores = [], [], []
    preds, true_labels = [], []
    for oidx, (train, test) in enumerate(cv):
        y_train, y_test = y[train], y[test]
        X_train, X_test = X[train, :], X[test, :]

        search.fit(X_train, y_train)
        clf = search.best_estimator_
        print search.best_params_

        clf.fit(X_train, y_train)
        train_scores.append(accuracy_score(clf.predict(X_train), y_train))
        test_scores.append(accuracy_score(clf.predict(X_test), y_test))
        dumb.fit(X_train, y_train)
        dummy_scores.append(accuracy_score(dumb.predict(X_test), y_test))
        preds += list(clf.predict(X_test))
        true_labels += list(y_test)
    return test_scores, train_scores, dummy_scores, preds, true_labels


phen = np.recfromcsv(home + '/data/overlap_resting/subjs.csv')
my_groups = ['NV', 'persistent', 'remission']

fdata_dir = home + '/data/fmri_example11/ica/dual_regression/'
fres_dir = home + '/data/fmri_example11/ica/results_zscore/'
fres_fname = ['clustmaskInNet_p99a99Corr_hiAgeGender_inNet_IC18_drStage2Z.nii',
              'clustmaskInNet_p95a95Corr_inattAgeGender_inNet_IC23_drStage2Z.nii']

mdata_dir = home + '/data/meg/ica/subj_zscores/'
mres_dir = mdata_dir + '/results/'
mres_fname = ['clustmaskInNet_p99a99_hiAgeGender_inNet_13-30_IC11_rtoz.nii',
              'clustmaskInNet_p99a95_inattAgeGender_inNet_4-8_IC07_rtoz.nii',
              'clustmaskInNet_p99a95_inattAgeGender_inNet_4-8_IC10_rtoz.nii',
              'clustmaskInNet_p99a95_inattAgeGender_inNet_8-13_IC04_rtoz.nii',
              'clustmaskInNet_p99a95_inattAgeGender_inNet_8-13_IC05_rtoz.nii',
              'clustmaskInNet_p99a95_inattAgeGender_inNet_8-13_IC09_rtoz.nii']

sx = [rec[2] for rec in phen]
inatt = [rec[3] for rec in phen]
hi = [rec[4] for rec in phen]
total = [i + j for i, j in zip(inatt, hi)]

# open fMRI data
fmri = []  # list of data per cluster
print 'Loading fMRI data'
for res in fres_fname:
    mask = nb.load(fres_dir + res)
    cl_values = np.unique(mask.get_data())[1:]  # remove 0
    nclusters = max(cl_values)
    ic = res.split('IC')[-1][:2]
    for c in range(nclusters):
        cl_data = []
        gv = mask.get_data() == cl_values[c]
        for rec in phen:
            fname = '%s/dr_stage2_%04d_Z.nii.gz' % (fdata_dir, rec[0])
            img = nb.load(fname)
            subj_data = img.get_data()[gv, int(ic)]  # load beta coefficients
            cl_data.append(float(np.nanmean(subj_data)))
    fmri.append(cl_data)
# makes fmri subjs x result
fmri = np.array(fmri).T

# open MEG data
meg = []  # list of data per cluster
print 'Loading MEG data'
for res in mres_fname:
    mask = nb.load(mres_dir + res)
    cl_values = np.unique(mask.get_data())[1:]  # remove 0
    nclusters = max(cl_values)
    freq_band = res.split('_')[-3]
    ic = res.split('IC')[-1][:2]
    for c in range(nclusters):
        cl_data = []
        gv = mask.get_data() == cl_values[c]
        for rec in phen:
            fname = '%s/%s_%s_alwaysPositive_IC%s_rtoz.nii' % (mdata_dir, rec[1], freq_band, ic)
            img = nb.load(fname)
            subj_data = img.get_data()[gv]  # load correlation
            cl_data.append(float(np.nanmean(subj_data)))
        meg.append(cl_data)
meg = np.array(meg).T

le = preprocessing.LabelEncoder()
y = le.fit_transform(sx)
F = preprocessing.scale(fmri)
M = preprocessing.scale(meg)

from sklearn.metrics import accuracy_score
from sklearn.dummy import DummyClassifier
clf = lda.LDA()
from sklearn.decomposition import RandomizedPCA, FactorAnalysis, FastICA

mtest_scores, mtrain_scores, mdummy_scores = [], [], []

ncomp = min(F.shape[1], M.shape[1])
pca = RandomizedPCA(n_components=ncomp, whiten=True)
ica = FastICA(n_components=ncomp)
if F.shape[1] > ncomp:
    Ft = pca.fit_transform(F)
else:
    Ft = F
if M.shape[1] > ncomp:
    Mt = pca.fit_transform(M)
else:
    Mt = M
both = pca.fit_transform(np.hstack([F, M]))
btest, btrain, bdumb, bpreds, btrue = get_scores(both, y)
ftest, ftrain, fdumb, fpreds, ftrue = get_scores(Ft, y)
mtest, mtrain, mdumb, mpreds, mtrue = get_scores(Mt, y)
both = ica.fit_transform(np.hstack([F, M]))
b2test, b2train, b2dumb, b2preds, b2true = get_scores(both, y)

# plotting results
nfeats = np.arange(ncomp)
bar_width = .25
colors = ['r', 'g', 'b']
fig = pl.figure()
n = len(ftest)
pl.subplot(1, 3, 1)
pl.bar(range(3), [np.mean(fdumb), np.mean(mdumb), np.mean(bdumb)],
       align='center')
pl.ylim(0, 1)
pl.title('Dummy')
pl.xticks(range(3), ['fMRI', 'MEG', 'PCA'])
pl.subplot(1, 3, 2)
pl.bar(range(4), [np.mean(ftrain), np.mean(mtrain),
                  np.mean(btrain), np.mean(b2train)],
       yerr=[np.nanstd(ftrain)/np.sqrt(n), np.nanstd(mtrain)/np.sqrt(n),
             np.nanstd(btrain)/np.sqrt(n), np.nanstd(b2train)/np.sqrt(n)],
       ecolor='r', align='center')
pl.ylim(0, 1)
pl.title('Train')
pl.xticks(range(4), ['fMRI', 'MEG', 'Both', 'ICA'])
pl.subplot(1, 3, 3)
pl.bar(range(4), [np.mean(ftest), np.mean(mtest),
                  np.mean(btest), np.mean(b2test)],
       yerr=[np.nanstd(ftest)/np.sqrt(n), np.nanstd(mtest)/np.sqrt(n),
             np.nanstd(btest)/np.sqrt(n), np.nanstd(b2test)/np.sqrt(n)],
       ecolor='r', align='center')
pl.ylim(0, 1)
pl.title('Test')
pl.xticks(range(4), ['fMRI', 'MEG', 'PCA', 'ICA'])

# do some ttests
print 'fMRI VS MEG = %.3f' % stats.ttest_ind(ftest, mtest)[1]
print 'fMRI VS PCA = %.3f' % stats.ttest_ind(ftest, btest)[1]
print 'MEG VS PCA = %.3f' % stats.ttest_ind(mtest, btest)[1]

# print sensitivity and specificity
from sklearn.metrics import classification_report
target_names = le.classes_
print '==== fMRI ===='
print(classification_report(ftrue, fpreds, target_names=target_names))
print '==== MEG ===='
print(classification_report(mtrue, mpreds, target_names=target_names))
print '==== PCA ===='
print(classification_report(btrue, bpreds, target_names=target_names))
print '==== ICA ===='
print(classification_report(b2true, b2preds, target_names=target_names))
