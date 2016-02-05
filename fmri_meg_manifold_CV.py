# computes the kCCA then LDA manifolds for MEG and fMRI, no CVs
import os
home = os.path.expanduser('~')
import pandas as pd
import statsmodels.formula.api as smf
import numpy as np
import re
from sklearn.decomposition import RandomizedPCA
import pylab as pl
import sys
sys.path.append(home + '/research_code/PyKCCA-master/')


# results are organized by groups. These groups can be seeds or networks, and they determine the individual plots that will be made, in addition to the global plot
results = {}

results['meg'] = [['affective_lACC_30to55_a0.05t0.99d5p5000.txt',
                   'affective_rParahippo_4to8_a0.05t0.99d5p5000.txt',
                   'cognitive_lDLPFC_1to4_a0.05t0.99d5p5000.txt',
                   'cognitive_rDLPFC_65to100_a0.05t0.99d5p5000.txt',
                   'cognitive_rSupra_65to100_a0.05t0.99d5p5000.txt',
                   'dmn_lACC_30to55_a0.05t0.99d5p5000.txt',
                   'dmn_lTPJ_4to8_a0.05t0.99d5p5000.txt',
                   'dmn_rACC_1to4_a0.05t0.99d5p5000.txt',
                   'dorsal_lFusiform_1to4_a0.05t0.99d5p5000.txt',
                   'dorsal_rFusiform_4to8_a0.05t0.99d5p5000.txt',
                   'dorsal_rFusiform_65to100_a0.05t0.99d5p5000.txt',
                   'ventral_lCingulate_4to8_a0.05t0.99d5p5000.txt',
                   'ventral_rVFC_30to55_a0.05t0.99d5p5000.txt',
                   'ventral_rVFC_4to8_a0.05t0.99d5p5000.txt']]

results['fmri'] = [['cognitive_lSupra_a0.05t0.99d5p5000.txt',
                    'cognitive_rSupra_a0.05t0.99d5p5000.txt',
                    'dmn_rACC_a0.05t0.99d5p5000.txt',
                    'dmn_rPrecuneus_a0.05t0.99d5p5000.txt',
                    'dorsal_lIPS_a0.05t0.99d5p5000.txt']]


phen = np.recfromcsv(home + '/data/overlap_resting/subjs.csv')

# # load the fMRI result and the data. Transform the data, remove residuals, and concatenate to the others in the the same group
# data_dir = home + '/data/results/inatt_resting/'
# subjs_fname = home + '/data/fmri/joel_all.txt'
# gf_fname = home + '/data/fmri/gf.csv'
# fid = open(subjs_fname, 'r')
# subjs = [line.rstrip() for line in fid]
# fid.close()
# gf = pd.read_csv(gf_fname)

# # the order of subjects in data is the same as in subjs, because that's how data was created. let's find that order in the gf and resort it
# idx = [np.nonzero(gf.maskid == int(s))[0][0] for s in subjs]
# gf = gf.iloc[idx]

# # find out what are the indices of subjects in overlap group
# overlap_idx = [np.nonzero(gf.maskid == s)[0][0] for s in phen['mask_id']]
# gf = gf.iloc[overlap_idx]

# good_data = {}
# gfs = {}
# good_data['fmri'] = []
# for group in results['fmri']:
#     group_data = []
#     for res in group:
#         seed = '_'.join(res.split('_')[:2])
#         print 'Loading data for %s' % res
#         data = np.genfromtxt(data_dir + '%s.txt' % seed)
#         # remove x,y,z and i,j,k, and change it to be subjs x voxels
#         data = data[:, 6:].T

#         # loading the result and keeping only the good voxels
#         mask = np.genfromtxt(data_dir + res)
#         # we assume all voxels, regardless of clusters, do the same thing
#         good_voxels = np.nonzero(mask[:, 3] > 0)[0]

#         X = np.arctanh(data[:, good_voxels])

#         # keep only subjects that belong to the overlap group
#         X = X[overlap_idx, :]

#         # remove voxels with NaNs
#         idx = np.isnan(X).any(axis=0)  # mask of features with at least 1 NaN
#         X = X[:, ~idx]
#         nfeats = X.shape[1]
#         Y_resid = X

#         # # let's grab the residuals now
#         # print 'Calculating residuals...'
#         # col_names = ['v%d' % i for i in range(nfeats)]
#         # # uses the same index so we don't have issues concatenating later
#         # data_df = pd.DataFrame(X, columns=col_names, index=gf.index, dtype=float)
#         # df = pd.concat([gf, data_df], axis=1)
#         # Y_resid = np.empty_like(X)
#         # Y_resid[:] = np.nan  # this way we keep the nan entries as is
#         # for v in range(nfeats):
#         #     keep = np.nonzero(~np.isnan(df['v%d' % v]))[0]
#         #     est = smf.ols(formula='v%d ~ age + gender' % v, data=df.iloc[keep]).fit()
#         #     Y_resid[np.array(keep), v] = est.resid
#         group_data.append(Y_resid)
#     good_data['fmri'].append(np.concatenate(group_data, axis=1))
# gfs['fmri'] = gf.copy()


# # do the same as above, now for MEG data
# data_dir = home + '/data/results/inatt_resting/'
# gf_fname = home + '/data/meg/gf.csv'

# good_data['meg'] = []
# for group in results['meg']:
#     group_data = []
#     for res in group:
#         gf = pd.read_csv(gf_fname)  # we keep re-sorting it (necessary?)

#         seed = '_'.join(res.split('_')[:3])
#         print 'Loading data for %s' % res
#         ds_data = np.load(data_dir + '/%s.npy' % (seed))[()]

#         # just making sure data nd gf are in the same order
#         subjs = []
#         data = []
#         for s, d in ds_data.iteritems():
#             data.append(d.T)
#             subjs.append(s)
#         X = np.arctanh(np.array(data).squeeze())

#         # the order of subjects in data is the same as in subjs
#         # let's find that order in the gf and resort it
#         idx = [np.nonzero(gf.maskid == s)[0][0] for s in subjs]
#         gf = gf.iloc[idx]

#         # find out what are the indices of subjects in overlap group
#         overlap_idx = [np.nonzero(gf.maskid == s)[0][0] for s in phen['meg_id']]
#         gf = gf.iloc[overlap_idx]
#         X = X[overlap_idx, :]

#         # loading the result and keeping only the good voxels
#         mask = np.genfromtxt(data_dir + res)
#         # we assume all voxels, regardless of clusters, do the same thing
#         good_voxels = np.nonzero(mask[:, 3] > 0)[0]

#         X = X[:, good_voxels]
#         # remove voxels with NaNs
#         idx = np.isnan(X).any(axis=0)  # mask of features with at least 1 NaN
#         X = X[:, ~idx]
#         nfeats = X.shape[1]
#         Y_resid = X

#         # # let's grab the residuals now
#         # print 'Calculating residuals...'
#         # col_names = ['v%d' % i for i in range(nfeats)]
#         # # uses the same index so we don't have issues concatenating later
#         # data_df = pd.DataFrame(X, columns=col_names, index=gf.index, dtype=float)
#         # df = pd.concat([gf, data_df], axis=1)
#         # Y_resid = np.empty_like(X)
#         # Y_resid[:] = np.nan  # this way we keep the nan entries as is
#         # for v in range(nfeats):
#         #     keep = np.nonzero(~np.isnan(df['v%d' % v]))[0]
#         #     est = smf.ols(formula='v%d ~ age + gender' % v, data=df.iloc[keep]).fit()
#         #     Y_resid[np.array(keep), v] = est.resid
#         group_data.append(Y_resid)
#     good_data['meg'].append(np.concatenate(group_data, axis=1))
# gfs['meg'] = gf.copy()


# since the overlap subjects are sorted, sx is the same for MEG and fMRI
groups = gfs['fmri'].group.tolist()
idx = [i for i, v in enumerate(groups) if v in ['remission', 'persistent']]
colors = np.array(gfs['fmri'].iloc[idx].group)
colors[colors == 'remission'] = 'b'
colors[colors == 'persistent'] = 'r'
colors[colors == 'NV'] = 'g'

from sklearn import lda, preprocessing
le = preprocessing.LabelEncoder()
le.fit(colors)
y = le.transform(colors)

# for each group, compute PCA for meg, fmri, and combined. Do the regression and calculate metric
nsubjs = len(y)
ncomps = range(5, nsubjs-10, 5)
nrows = ceil(sqrt(len(ncomps)))
ncols = ceil(len(ncomps)/nrows)
ngroups = len(good_data['fmri'])


def centeroid(arr):
    length = arr.shape[0]
    sum_x = np.sum(arr[:, 0])
    sum_y = np.sum(arr[:, 1])
    return sum_x/length, sum_y/length


# score is the added distance between centroids, over the mean distance within centroids
def get_score(arr_train, arr_test, labels_train, labels_test):
    c1 = centeroid(Y[colors == 'r', :])
    c2 = centeroid(Y[colors == 'g', :])
    c3 = centeroid(Y[colors == 'b', :])
    d1 = np.sqrt((Y[colors == 'r', 0] - c1[0])**2 +
                 (Y[colors == 'r', 1] - c1[1])**2)
    d2 = np.sqrt((Y[colors == 'g', 0] - c2[0])**2 +
                 (Y[colors == 'g', 1] - c2[1])**2)
    d3 = np.sqrt((Y[colors == 'b', 0] - c3[0])**2 +
                 (Y[colors == 'b', 1] - c3[1])**2)
    score = (np.sqrt((c1[0] - c2[0])**2 + (c1[1] - c2[1])**2) +
             np.sqrt((c1[0] - c3[0])**2 + (c1[1] - c3[1])**2) +
             np.sqrt((c3[0] - c2[0])**2 + (c3[1] - c2[1])**2)) / float(d1.mean() + d2.mean() + d3.mean())
    return score


import kcca
import kernels
from sklearn.cross_validation import ShuffleSplit
from sklearn import lda
nobs = len(idx)
nfolds = 50
cv = ShuffleSplit(nobs, n_iter=nfolds, test_size=.1)
max_comps = range(2, cv.n_train, 2)

for g in range(ngroups):
    X_meg = preprocessing.scale(good_data['fmri'][g][idx, :])
    X_fmri = preprocessing.scale(good_data['meg'][g][idx, :])
    kernel = kernels.LinearKernel()
    cca = kcca.KCCA(kernel, kernel, regularization=1e-5, decomp='full',
                    method='kettering_method', scaler1=lambda x: x,
                    scaler2=lambda x: x)
    cca = cca.fit(X_fmri, X_meg)
    X_fmri2, X_meg2 = cca.transform(X_fmri, X_meg)

    cnt = 1
    pl.figure()
    all_ym, all_yf, all_yc = [], [], []
    for c in max_comps:
        print c
        yc, yf, ym = [], [], []
        for oidx, (train, test) in enumerate(cv):
            X_fmri_train = X_fmri[train]
            X_fmri_test = X_fmri[test]
            X_meg_train = X_meg[train]
            X_meg_test = X_meg[test]
            y_train = y[train]
            y_test = y[test]

            pca = RandomizedPCA(n_components=c, whiten=True)
            clf = lda.LDA(n_components=2)

            cca = cca.fit(X_fmri_train, X_meg_train)
            X_train1, X_train2 = cca.transform(X_fmri_train, X_meg_train)
            X_test1, X_test2 = cca.transform(X_fmri_test, X_meg_test)
            Y_train = clf.fit_transform(X_train2[:, :c], y_train)
            yc.append(clf.score(X_test2[:, :c], y_test))

            X_train = pca.fit_transform(X_fmri_train)
            Y_train = clf.fit_transform(X_train, y_train)
            X_test = pca.transform(X_fmri_test)
            yf.append(clf.score(X_test, y_test))

            X_train = pca.fit_transform(X_meg_train)
            Y_train = clf.fit_transform(X_train, y_train)
            X_test = pca.transform(X_meg_test)
            ym.append(clf.score(X_test, y_test))

            # X_train = pca.fit_transform(np.hstack([X_fmri_train, X_meg_train]))
            # Y_train = clf.fit_transform(X_train, y_train)
            # X_test = pca.transform(np.hstack([X_fmri_test, X_meg_test]))
            # yc.append(clf.score(X_test, y_test))

        all_ym.append(np.mean(ym))
        all_yf.append(np.mean(yf))
        all_yc.append(np.mean(yc))
    fig = pl.figure()
    pl.plot(max_comps, all_yf, max_comps, all_ym, max_comps, all_yc)
    pl.xlabel('ncomps')
    pl.ylabel('Score')
    pl.legend(['fMRI', 'MEG', 'combined'], loc='best')
    pl.title('Group %d' % g)
