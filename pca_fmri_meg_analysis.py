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

# load the fMRI result and the data. Transform the data, remove residuals, and concatenate to the others in the the same group
data_dir = home + '/data/results/inatt_resting/'
subjs_fname = home + '/data/fmri/joel_all.txt'
gf_fname = home + '/data/fmri/gf.csv'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
gf = pd.read_csv(gf_fname)

# the order of subjects in data is the same as in subjs, because that's how data was created. let's find that order in the gf and resort it
idx = [np.nonzero(gf.maskid == int(s))[0][0] for s in subjs]
gf = gf.iloc[idx]

# find out what are the indices of subjects in overlap group
overlap_idx = [np.nonzero(gf.maskid == s)[0][0] for s in phen['mask_id']]
gf = gf.iloc[overlap_idx]

good_data = {}
gfs = {}
good_data['fmri'] = []
for group in results['fmri']:
    group_data = []
    for res in group:
        seed = '_'.join(res.split('_')[:2])
        print 'Loading data for %s' % res
        data = np.genfromtxt(data_dir + '%s.txt' % seed)
        # remove x,y,z and i,j,k, and change it to be subjs x voxels
        data = data[:, 6:].T

        # loading the result and keeping only the good voxels
        mask = np.genfromtxt(data_dir + res)
        # we assume all voxels, regardless of clusters, do the same thing
        good_voxels = np.nonzero(mask[:, 3] > 0)[0]

        X = np.arctanh(data[:, good_voxels])

        # keep only subjects that belong to the overlap group
        X = X[overlap_idx, :]

        # remove voxels with NaNs
        idx = np.isnan(X).any(axis=0)  # mask of features with at least 1 NaN
        X = X[:, ~idx]
        nfeats = X.shape[1]
        Y_resid = X

        # # let's grab the residuals now
        # print 'Calculating residuals...'
        # col_names = ['v%d' % i for i in range(nfeats)]
        # # uses the same index so we don't have issues concatenating later
        # data_df = pd.DataFrame(X, columns=col_names, index=gf.index, dtype=float)
        # df = pd.concat([gf, data_df], axis=1)
        # Y_resid = np.empty_like(X)
        # Y_resid[:] = np.nan  # this way we keep the nan entries as is
        # for v in range(nfeats):
        #     keep = np.nonzero(~np.isnan(df['v%d' % v]))[0]
        #     est = smf.ols(formula='v%d ~ age + gender' % v, data=df.iloc[keep]).fit()
        #     Y_resid[np.array(keep), v] = est.resid
        group_data.append(Y_resid)
    good_data['fmri'].append(np.concatenate(group_data, axis=1))
gfs['fmri'] = gf.copy()


# do the same as above, now for MEG data
data_dir = home + '/data/results/inatt_resting/'
gf_fname = home + '/data/meg/gf.csv'

good_data['meg'] = []
for group in results['meg']:
    group_data = []
    for res in group:
        gf = pd.read_csv(gf_fname)  # we keep re-sorting it (necessary?)

        seed = '_'.join(res.split('_')[:3])
        print 'Loading data for %s' % res
        ds_data = np.load(data_dir + '/%s.npy' % (seed))[()]

        # just making sure data nd gf are in the same order
        subjs = []
        data = []
        for s, d in ds_data.iteritems():
            data.append(d.T)
            subjs.append(s)
        X = np.arctanh(np.array(data).squeeze())

        # the order of subjects in data is the same as in subjs
        # let's find that order in the gf and resort it
        idx = [np.nonzero(gf.maskid == s)[0][0] for s in subjs]
        gf = gf.iloc[idx]

        # find out what are the indices of subjects in overlap group
        overlap_idx = [np.nonzero(gf.maskid == s)[0][0] for s in phen['meg_id']]
        gf = gf.iloc[overlap_idx]
        X = X[overlap_idx, :]

        # loading the result and keeping only the good voxels
        mask = np.genfromtxt(data_dir + res)
        # we assume all voxels, regardless of clusters, do the same thing
        good_voxels = np.nonzero(mask[:, 3] > 0)[0]

        X = X[:, good_voxels]
        # remove voxels with NaNs
        idx = np.isnan(X).any(axis=0)  # mask of features with at least 1 NaN
        X = X[:, ~idx]
        nfeats = X.shape[1]
        Y_resid = X

        # # let's grab the residuals now
        # print 'Calculating residuals...'
        # col_names = ['v%d' % i for i in range(nfeats)]
        # # uses the same index so we don't have issues concatenating later
        # data_df = pd.DataFrame(X, columns=col_names, index=gf.index, dtype=float)
        # df = pd.concat([gf, data_df], axis=1)
        # Y_resid = np.empty_like(X)
        # Y_resid[:] = np.nan  # this way we keep the nan entries as is
        # for v in range(nfeats):
        #     keep = np.nonzero(~np.isnan(df['v%d' % v]))[0]
        #     est = smf.ols(formula='v%d ~ age + gender' % v, data=df.iloc[keep]).fit()
        #     Y_resid[np.array(keep), v] = est.resid
        group_data.append(Y_resid)
    good_data['meg'].append(np.concatenate(group_data, axis=1))
gfs['meg'] = gf.copy()


def regress_pcs(Y, sx, pcs):
    pca = RandomizedPCA(n_components=max(pcs), whiten=True).fit(Y)
    Y_pca = pca.transform(Y)
    col_names = ['pc%d' % i for i in range(max(pcs))]
    df = pd.DataFrame(Y_pca, columns=col_names, dtype=float)
    y = []
    for x in pcs:
        formula = 'sx ~ ' + '+'.join(['pc%d' % i for i in range(x)])
        est = smf.ols(formula=formula, data=df).fit()
        y.append(est.aic)
    return y


boot = 0
ub = 97.5
lb = 2.5
# since the overlap subjects are sorted, sx is the same for MEG and fMRI
groups = gfs['fmri'].group.tolist()
idx = [i for i, v in enumerate(groups) if v in ['remission', 'persistent']]
sx = np.array(gfs['fmri'].iloc[idx].inatt)

# for each group, compute PCA for meg, fmri, and combined. Do the regression and calculate metric
nsubjs = len(sx)
pcs = range(1, nsubjs, 3)
ngroups = len(good_data['fmri'])

for g in range(ngroups):
    yf = regress_pcs(good_data['fmri'][g][idx, :], sx, pcs)
    ym = regress_pcs(good_data['meg'][g][idx, :], sx, pcs)
    yc = regress_pcs(np.hstack([good_data['fmri'][g][idx, :],
                                good_data['meg'][g][idx, :]]),
                     sx, pcs)

    fig = pl.figure()
    pl.plot(pcs, yf, pcs, ym, pcs, yc)
    pl.legend(['fMRI', 'MEG', 'combined'], loc='best')
    if boot > 0:
        yfb = np.empty([boot, len(yf)])
        ymb = np.empty([boot, len(ym)])
        ycb = np.empty([boot, len(yc)])
        yfb[:] = np.nan
        ymb[:] = np.nan
        ycb[:] = np.nan
        for i in range(boot):
            print 'Bootstrap', i + 1, '/', boot
            idx = np.random.choice(nsubjs, nsubjs)
            yfb[i, :] = regress_pcs(good_data['fmri'][g][idx, :],
                                    sx.iloc[idx], pcs)
            ymb[i, :] = regress_pcs(good_data['meg'][g][idx, :],
                                    sx.iloc[idx], pcs)
            ycb[i, :] = regress_pcs(np.hstack([good_data['fmri'][g][idx, :],
                                               good_data['meg'][g][idx, :]]),
                                    sx.iloc[idx], pcs)
        # figure out the 95th percentile
        pl.fill_between(pcs, np.percentile(yfb, ub, axis=0),
                        np.percentile(yfb, lb, axis=0),
                        facecolor='blue', alpha=.3)
        pl.fill_between(pcs, np.percentile(ymb, ub, axis=0),
                        np.percentile(ymb, lb, axis=0),
                        facecolor='green', alpha=.3)
        pl.fill_between(pcs, np.percentile(ycb, ub, axis=0),
                        np.percentile(ycb, lb, axis=0),
                        facecolor='red', alpha=.3)
    pl.xlabel('PCs')
    pl.ylabel('Model goodness')
    pl.title('group %d' % (g+1))

# # do the same as above for the combination of all groups
# yf = regress_pcs(np.concatenate(good_data['fmri'], axis=1), sx, pcs)
# ym = regress_pcs(np.concatenate(good_data['meg'], axis=1), sx, pcs)
# yc = regress_pcs(np.hstack([np.concatenate(good_data['fmri'], axis=1),
#                             np.concatenate(good_data['meg'], axis=1)]),
#                  sx, pcs)
# fig = pl.figure()
# pl.plot(pcs, yf, pcs, ym, pcs, yc)
# pl.xlabel('PCs')
# pl.ylabel('Model goodness')
# pl.legend(['fMRI', 'MEG', 'combined'], loc='best')
# pl.title('all groups')

# MAKE OPTION TO SELECT WITH OR WITHOUT NVS
# TRY DIFFERENT COMBINATIONS OF MEG AND FMRI? PLS, CCA?
# TRY ROOT MEAN SQUARED LOOCV EVALUATION
