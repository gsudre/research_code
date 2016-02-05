''' Checks whether there is a difference in the seed connectivity using OLS with covariates '''

import numpy as np
import os
home = os.path.expanduser('~')
import pandas as pd
import statsmodels.formula.api as smf
import nibabel as nb
import sys


if len(sys.argv) > 1:
    comp = int(sys.argv[1])
    test = sys.argv[2]
else:
    comp = 25
    test = 'hi'

alpha = .05
gf_fname = home + '/data/fmri_example11/gf.csv'
subjs_fname = home+'/data/fmri_example11/all.txt'
# data_dir = home + '/data/fmri/ica/dual_regression_alwaysPositive_AllSubjsZeroFilled_scaled/'
data_dir = home + '/data/fmri_example11/ica/dual_regression/'
# res_dir = home + '/data/fmri/ica/results_zscore/'
res_dir = home + '/data/fmri_example11/ica/results_zscore/'
# mask_fname = home + '/data/fmri/downsampled_444/gm_fast_444.nii'
# mask_fname = home + '/data/fmri/downsampled_444/mask_GM_resam.nii'
# mask_fname = home + '/data/fmri/downsampled_444/automask_444.nii'
mask_fname = home + '/data/fmri_example11/brain_mask_444.nii'
mask_fname = home + '/data/fmri_example11/ica/results_zscore/IC%02d_binNetMask_p01BF.nii' % comp

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
gf = pd.read_csv(gf_fname)

if test.find('WithNVs') >= 0:
    sx = test.replace('WithNVs', '')
    target_groups = ['NV', 'persistent', 'remission']
else:
    sx = test
    target_groups = ['persistent', 'remission']

# the order of subjects in data is the same as in subjs
# let's find that order in the gf and resort it
idx = [np.nonzero(gf.maskid == int(s))[0][0] for s in subjs]
gf = gf.iloc[idx]

mask = nb.load(mask_fname)
# good voxels
gv = mask.get_data() > 0
gv = gv.flatten()
nvoxels = np.sum(gv)

# note that the concatenated .nii file was created with the same subject order as joel_all.txt!
data = np.zeros([len(subjs), nvoxels])
data[:] = np.nan
print 'Loading data: comp %d' % comp
for s, subj in enumerate(subjs):
    img = nb.load(data_dir + 'dr_stage2_%s_Z.nii.gz' % subj)
    subj_data = img.get_data()[:, :, :, comp].flatten()
    data[s, :] = subj_data[gv]
print 'Running tests...'
col_names = ['v%d' % i for i in range(nvoxels)]
# uses the same index so we don't have issues concatenating later
data_df = pd.DataFrame(data, columns=col_names, index=gf.index, dtype=float)
df = pd.concat([gf, data_df], axis=1)

# selecting just specific groups
groups = gf.group.tolist()
idx = [i for i, v in enumerate(groups) if v in target_groups]

res = np.zeros([gv.shape[0], 4])  # ttest, pval, beta, cc
res[:] = np.nan
gv_idx = np.nonzero(gv)[0]
pvals = []
for v in range(nvoxels):
    print '%d / %d' % (v + 1, nvoxels)
    good_subjs = np.nonzero(~np.isnan(df['v%d' % v]))[0]
    keep = np.intersect1d(good_subjs, idx)
    est = smf.ols(formula='v%d ~ %s + age + gender' % (v, sx), data=df.iloc[keep]).fit()
    # convert from coefficient to beta
    beta = est.params[sx]
    cc = beta * np.std(df.iloc[keep][sx]) / np.std(df.iloc[keep]['v%d' % v])
    res[gv_idx[v], 0] = est.tvalues[sx]
    res[gv_idx[v], 1] = 1 - est.pvalues[sx]
    res[gv_idx[v], 2] = beta
    res[gv_idx[v], 3] = cc
    pvals.append(est.pvalues[sx])
fname = '%s/%sAgeGender_inNet_IC%02d_drStage2Z.nii' % (res_dir, test, comp)
print 'Saving results to %s' % fname
res = res.reshape(mask.get_data().shape[:3] + tuple([-1]))
nb.save(nb.Nifti1Image(res, img.get_affine()), fname)

from mne.stats import fdr_correction
reject_fdr, pval_fdr = fdr_correction(pvals, alpha=alpha, method='indep')
