''' Checks whether there is a difference in the seed connectivity using OLS with covariates '''

import numpy as np
import os
home = os.path.expanduser('~')
import pandas as pd
import statsmodels.formula.api as smf
import nibabel as nb
import glob
from scipy import stats


bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
gf_fname = home + '/data/meg/gf.csv'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = home + '/data/meg/ica/'
adjust = True
test_fname = 'perVSrem'
test_groups = ['persistent', 'remission']

if adjust:
    test_fname = test_fname + 'AgeGender'
vox_pos = np.genfromtxt(home + '/data/meg/sam_narrow_8mm/voxelsInBrain888.txt', delimiter=' ')
nvoxels = vox_pos.shape[0]

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
gf = pd.read_csv(gf_fname)

# the order of subjects in data is the same as in subjs
# let's find that order in the gf and resort it
idx = [np.nonzero(gf.maskid == s)[0][0] for s in subjs]
gf = gf.iloc[idx]

for bidx, band in enumerate(bands):
    fname = '%s/%s_%d-%d_IC*.nii' % (data_dir, subjs[0], band[0], band[1])
    ncomps = len(glob.glob(fname))
    for c in range(ncomps):
        data = np.zeros([len(subjs), nvoxels])
        data[:] = np.nan
        print 'Loading data: comp %d' % c, band
        for sidx, s in enumerate(subjs):
            fname = '%s/%s_%d-%d_IC%02d.nii' % (data_dir, s, band[0],
                                                band[1], c)
            img = nb.load(fname)
            # subj_data = img.get_data()[:, :, :, 0]  # load beta coefficients
            subj_data = img.get_data()[:, :, :, 2]  # load correlation coefficients
            for v in range(nvoxels):
                data[sidx, v] = subj_data[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2])]
        print 'Running tests...'
        col_names = ['v%d' % i for i in range(nvoxels)]
        # uses the same index so we don't have issues concatenating later
        data_df = pd.DataFrame(data, columns=col_names, index=gf.index, dtype=float)
        df = pd.concat([gf, data_df], axis=1)

        # selecting just specific groups
        groups = gf.group.tolist()
        idx = [i for i, v in enumerate(groups) if v in test_groups]

        res = np.zeros(img.get_data().shape[:3] + tuple([2]))  # test and pval
        res[:] = np.nan
        for v in range(nvoxels):
            good_subjs = np.nonzero(~np.isnan(df['v%d' % v]))[0]
            keep = np.intersect1d(good_subjs, idx)
            if not adjust:
                g0 = np.nonzero(df.iloc[keep]['group'] == test_groups[0])[0]
                x = np.array(df.iloc[keep]['v%d' % v])[g0]
                g1 = np.nonzero(df.iloc[keep]['group'] == test_groups[1])[0]
                y = np.array(df.iloc[keep]['v%d' % v])[g1]
            else:
                est = smf.ols(formula='v%d ~ age + gender' % v, data=df.iloc[keep]).fit()
                resid = np.array(est.resid)
                g0 = np.nonzero(df.iloc[keep]['group'] == test_groups[0])[0]
                x = resid[g0]
                g1 = np.nonzero(df.iloc[keep]['group'] == test_groups[1])[0]
                y = resid[g1]
            if len(x) == 0 or len(y) == 0:
                res[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), 0] = 0
                res[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), 1] = 0
            else:
                [u, prob] = stats.mannwhitneyu(x, y)
                # make it two-tailed
                res[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), 0] = u
                res[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), 1] = 1 - prob / 2
        fname = '%s/results_correlation/MW%s_%d-%d_IC%02d.nii' % (data_dir, test_fname, band[0], band[1], c)
        print 'Saving results to %s' % fname
        nb.save(nb.Nifti1Image(res, img.get_affine()), fname)
