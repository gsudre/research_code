''' Checks whether there is a difference in the seed connectivity using OLS with covariates '''

import numpy as np
import os
home = os.path.expanduser('~')
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
import nibabel as nb
import sys


if len(sys.argv) > 1:
    comp = int(sys.argv[1])
else:
    comp = 1

gf_fname = home + '/data/fmri_example11/gf.csv'
subjs_fname = home+'/data/fmri_example11/all.txt'
data_dir = home + '/data/fmri_example11/ica/dual_regression/'
res_dir = home + '/data/fmri_example11/ica/results_zscore/'
mask_fname = home + '/data/fmri_example11/brain_mask_444.nii'
mask_fname = home + '/data/fmri_example11/ica/results_zscore/IC%02d_binNetMask_p01BF.nii' % comp

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
gf = pd.read_csv(gf_fname)

# the order of subjects in data is the same as in subjs
# let's find that order in the gf and resort it
idx = [np.nonzero(gf.maskid == int(s))[0][0] for s in subjs]
gf = gf.iloc[idx]

mask = nb.load(mask_fname)
# good voxels
gv = mask.get_data().astype(bool).flatten()
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

res = np.zeros([gv.shape[0], 2])  # ttest and pval
res[:] = np.nan
gv_idx = np.nonzero(gv)[0]
for v in range(nvoxels):
    print '%d / %d' % (v + 1, nvoxels)
    keep = np.nonzero(~np.isnan(df['v%d' % v]))[0]
    est = smf.ols(formula='v%d ~ group + age + gender' % v, data=df.iloc[keep]).fit()
    an = anova_lm(est)
    res[gv_idx[v], 0] = an['F']['group']
    res[gv_idx[v], 1] = 1 - an['PR(>F)']['group']
fname = '%s/anovaAgeGender_inNet_IC%02d_drStage2Z.nii' % (res_dir, comp)
print 'Saving results to %s' % fname
res = res.reshape(mask.get_data().shape[:3] + tuple([-1]))
nb.save(nb.Nifti1Image(res, img.get_affine()), fname)
