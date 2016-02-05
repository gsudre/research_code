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
    test_fname = sys.argv[2]
    test_groups = [sys.argv[3], sys.argv[4]]
else:
    comp = 1
    test_fname = 'nvVSper'
    test_groups = ['NV', 'persistent']

gf_fname = home + '/data/fmri/gf.csv'
subjs_fname = home+'/data/fmri/joel_all.txt'
data_dir = home + '/data/fmri/ica/dual_regression_AllSubjsZeroFilled/'
res_dir = home + '/data/fmri/ica/results/'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
gf = pd.read_csv(gf_fname)

# the order of subjects in data is the same as in subjs
# let's find that order in the gf and resort it
idx = [np.nonzero(gf.maskid == int(s))[0][0] for s in subjs]
gf = gf.iloc[idx]

mask = nb.load(home + '/data/fmri/downsampled_444/brain_mask_444.nii')
# good voxels
gv = mask.get_data().astype(bool).flatten()
nvoxels = np.sum(gv)

# note that the concatenated .nii file was created with the same subject order as joel_all.txt!
data = np.zeros([len(subjs), nvoxels])
data[:] = np.nan
print 'Loading data: comp %d' % comp
for s, subj in enumerate(subjs):
    img = nb.load(data_dir + 'dr_stage2_%s.nii.gz' % subj)
    subj_data = img.get_data()[:, :, :, comp].flatten()
    data[s, :] = subj_data[gv]
print 'Running tests...'
col_names = ['v%d' % i for i in range(nvoxels)]
# uses the same index so we don't have issues concatenating later
data_df = pd.DataFrame(data, columns=col_names, index=gf.index, dtype=float)
df = pd.concat([gf, data_df], axis=1)

# selecting just specific groups
groups = gf.group.tolist()
idx = [i for i, v in enumerate(groups)
       if v in test_groups]

res = np.zeros([gv.shape[0], 3])  # ttest and pval
res[:] = np.nan
gv_idx = np.nonzero(gv)[0]
for v in range(nvoxels):
    good_subjs = np.nonzero(~np.isnan(df['v%d' % v]))[0]
    keep = np.intersect1d(good_subjs, idx)
    est = smf.ols(formula='v%d ~ group + age + gender' % v, data=df.iloc[keep]).fit()
    # find the coefficient with group term
    sx = [x for x, i in enumerate(est.tvalues.keys()) if i.find('group') == 0]
    if len(sx) > 0:
        sx = sx[0]
        # convert from coefficient to beta
        beta = est.tvalues[sx]
        res[gv_idx[v], 0] = beta
        res[gv_idx[v], 1] = 1 - est.pvalues[sx]
    else:
        res[gv_idx[v], 0] = 0
        res[gv_idx[v], 1] = 0
fname = '%s/%sAgeGender_IC%02d.nii' % (res_dir, test_fname, comp)
print 'Saving results to %s' % fname
res = res.reshape(mask.get_data().shape[:3] + tuple([-1]))
nb.save(nb.Nifti1Image(res, img.get_affine()), fname)
