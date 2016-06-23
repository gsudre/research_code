''' Checks if the voxel ICA results are significant in different regression tests '''

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
    test = sys.argv[2]
else:
    comp = 25
    test = 'hi'

alpha = .05
gf_fname = home + '/data/fmri/gf.csv'
subjs_fname = home+'/data/fmri/joel_all.txt'
data_dir = home + '/data/fmri_full_grid/melodic/dual/'
res_dir = home + '/data/fmri_full_grid/results/'
mask_fname = home + '/data/fmri_full_grid/brain_mask_full.nii'

# parsing the test
if len(sys.argv) > 3:  # ttest: comp, g1, g2
    test = sys.argv[2] + 'VS' + sys.argv[3]
    ind_vars = 'group + age + sex + mvmt + mvmt2'
    target_groups = [sys.argv[2], sys.argv[3]]
elif test.find('WithNVs') >= 0:
    sx = test.replace('WithNVs', '')
    ind_vars = sx + ' + age + sex + mvmt + mvmt2'
    target_groups = ['NV', 'persistent', 'remission']
elif test.find('anova') >= 0:
    sx = test
    ind_vars = 'group + age + sex + mvmt + mvmt2'
    target_groups = ['NV', 'persistent', 'remission']
else:
    sx = test
    ind_vars = sx + ' + age + sex + mvmt + mvmt2'
    target_groups = ['persistent', 'remission']

fname = '%s/%s_ageSexMvmtMvmt2_IC%02d_Z.nii' % (res_dir, test, comp)

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
df.rename(columns={'age^2': 'age2', 'mvmt^2': 'mvmt2'}, inplace=True)

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
    est = smf.ols(formula='v%d ~ %s' % (v, ind_vars), data=df.iloc[keep]).fit()
    if test == 'anova':
        an = anova_lm(est)
        res[gv_idx[v], 0] = an['F']['group']
        res[gv_idx[v], 1] = 1 - an['PR(>F)']['group']
    elif test.find('VS') > 0:
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
    else:
        # convert from coefficient to beta
        beta = est.params[sx]
        cc = beta * np.std(df.iloc[keep][sx]) / np.std(df.iloc[keep]['v%d' % v])
        res[gv_idx[v], 0] = est.tvalues[sx]
        res[gv_idx[v], 1] = 1 - est.pvalues[sx]
        res[gv_idx[v], 2] = beta
        res[gv_idx[v], 3] = cc
    pvals.append(1 - res[gv_idx[v], 1])  # saving for FDR later

print 'Saving results to %s' % fname
res = res.reshape(mask.get_data().shape[:3] + tuple([-1]))
nb.save(nb.Nifti1Image(res, img.get_affine()), fname)

from mne.stats import fdr_correction
reject_fdr, pval_fdr = fdr_correction(pvals, alpha=alpha, method='indep')
