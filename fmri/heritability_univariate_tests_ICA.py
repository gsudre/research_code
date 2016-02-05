''' Checks whether there is a correlation between symptom count and the voxels in the phenotype files '''

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
    comp = 1
    test = 'inattWithNVs'

data_dir = home + '/data/solar_familyAndRelativesAndAlone_household/'
data_fname = 'phen_IC%02d.csv' % comp
res_dir = data_dir + '/regression/'

df = pd.read_csv(data_dir + data_fname)

mask = nb.load(home + '/data/heritability_fmri/brain_mask_444.nii')
# good voxels
gv = mask.get_data().astype(bool).flatten()
nvoxels = np.sum(gv)

# selecting just specific groups
if test.find('WithNVs') > 0:
    idx = range(df.shape[0])
    sx = test.replace('WithNVs', '')
else:
    groups = df.group.tolist()
    idx = [i for i, v in enumerate(groups)
           if v in ['remission', 'persistent']]
    sx = test

res = np.zeros([gv.shape[0], 3])  # ttest and pval
res[:] = np.nan
gv_idx = np.nonzero(gv)[0]
for v in range(nvoxels):
    print v
    good_subjs = np.nonzero(~np.isnan(df['v%d' % v]))[0]
    keep = np.intersect1d(good_subjs, idx)
    est = smf.ols(formula='v%d ~ %s + age + sex' % (v, sx), data=df.iloc[keep]).fit()
    # convert from coefficient to beta
    beta = est.tvalues[sx]
    cc = beta * np.std(df.iloc[keep][sx]) / np.std(df.iloc[keep]['v%d' % v])
    res[gv_idx[v], 0] = beta
    res[gv_idx[v], 1] = 1 - est.pvalues[sx]
    res[gv_idx[v], 2] = cc
fname = '%s/%sAgeGender_IC%02d.nii' % (res_dir, test, comp)
print 'Saving results to %s' % fname
res = res.reshape(mask.get_data().shape[:3] + tuple([-1]))
nb.save(nb.Nifti1Image(res, mask.get_affine()), fname)
