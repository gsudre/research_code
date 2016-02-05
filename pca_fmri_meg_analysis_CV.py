import os
home = os.path.expanduser('~')
import pandas as pd
import statsmodels.formula.api as smf
import numpy as np
import re
from sklearn.decomposition import RandomizedPCA
import pylab as pl


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

#         Y_resid = X.copy()
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

#         Y_resid = X.copy()
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


def regress_pcs(Y, sx, pcs):
    pca = RandomizedPCA(n_components=max(pcs), whiten=True).fit(Y)
    Y_pca = pca.transform(Y)
    col_names = ['pc%d' % i for i in range(max(pcs))]
    df = pd.DataFrame(Y_pca, columns=col_names, dtype=float, index=sx.index)
    y = []
    for x in pcs:
        formula = 'sx ~ ' + '+'.join(['pc%d' % i for i in range(x)])
        est = smf.ols(formula=formula, data=df).fit()
        y.append(est.rsquared_adj)
    return y


from sklearn.cross_validation import ShuffleSplit
from sklearn.pls import PLSRegression
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error
from sklearn.preprocessing import scale
from sklearn.dummy import DummyRegressor

nobs = good_data['meg'][0].shape[0]
nfolds = 50
cv = ShuffleSplit(nobs, n_iter=nfolds, test_size=.1)
max_comps = range(2, cv.n_train, 2)

# Trying the prediction with different components
comp_scores = []
dumb_scores = []
yf = []
ym = []
ypca = []
yplsm = []
yplsf = []
X_fmri = scale(np.concatenate(good_data['fmri'], axis=1))
X_meg = scale(np.concatenate(good_data['meg'], axis=1))
for ncomp in max_comps:
    mse_fmri = []
    mse_meg = []
    mse_pca = []
    mse_plsm = []
    mse_plsf = []

    print 'Trying %d components' % ncomp
    plsca = PLSRegression(n_components=ncomp)
    dumb = DummyRegressor(strategy='mean')

    for oidx, (train, test) in enumerate(cv):
        X_fmri_train = X_fmri[train]
        X_fmri_test = X_fmri[test]
        X_meg_train = X_meg[train]
        X_meg_test = X_meg[test]
        y_train = sx.iloc[train].tolist()
        y_test = sx.iloc[test].tolist()

        pca = RandomizedPCA(n_components=ncomp, whiten=True)

        clf = LinearRegression().fit(pca.fit_transform(X_fmri_train), y_train)
        mse_fmri.append(mean_squared_error(clf.predict(pca.transform(X_fmri_test)), y_test))

        clf = LinearRegression().fit(pca.fit_transform(X_meg_train), y_train)
        mse_meg.append(mean_squared_error(clf.predict(pca.transform(X_meg_test)), y_test))

        both_train = np.hstack([X_meg_train, X_fmri_train])
        both_test = np.hstack([X_meg_test, X_fmri_test])

        clf = LinearRegression().fit(pca.fit_transform(both_train), y_train)
        mse_pca.append(mean_squared_error(clf.predict(pca.transform(both_test)), y_test))

        plsca.fit(X_meg_train, X_fmri_train)
        X_mc_train, X_fc_train = plsca.transform(X_meg_train, X_fmri_train)
        X_mc_test, X_fc_test = plsca.transform(X_meg_test, X_fmri_test)
        clf = LinearRegression().fit(X_mc_train, y_train)
        mse_plsm.append(mean_squared_error(clf.predict(X_mc_test), y_test))
        mse_plsf.append(mean_squared_error(clf.predict(X_fc_test), y_test))

        # dumb.fit(X_fmri_train, X_meg_train)
        # dumb_pred = dumb.predict(X_fmri_test)
        # dumb_mae += mean_absolute_error(X_meg_test,dumb_pred)

    yf.append(np.sqrt(np.mean(mse_fmri)))
    ym.append(np.sqrt(np.mean(mse_meg)))
    ypca.append(np.sqrt(np.mean(mse_pca)))
    yplsm.append(np.sqrt(np.mean(mse_plsm)))
    yplsf.append(np.sqrt(np.mean(mse_plsf)))
    # dumb_scores.append(dumb_mae/nfolds)

fig = pl.figure()
pl.plot(max_comps, yf, max_comps, ym, max_comps, ypca, max_comps, yplsm,
        max_comps, yplsf)
pl.xlabel('PCs')
pl.ylabel('Model error')
pl.legend(['fMRI', 'MEG', 'PCA', 'PLSM', 'PLSF'], loc='best')
pl.title('all groups')

# MAKE OPTION TO SELECT WITH OR WITHOUT NVS
# TRY DIFFERENT COMBINATIONS OF MEG AND FMRI? PLS, CCA?
# TRY ROOT MEAN SQUARED LOOCV EVALUATION
