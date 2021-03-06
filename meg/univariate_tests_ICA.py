''' Checks whether there is a difference in the seed connectivity using OLS with covariates '''

import numpy as np
import os
home = os.path.expanduser('~')
import pandas as pd
import statsmodels.formula.api as smf
import nibabel as nb
import glob


bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
# bands = [bands[-1]]
# comps = range(21)
test = 'total'
gf_fname = home + '/data/meg/gf.csv'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = home + '/data/meg/ica/subj_zscores/'
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

if test.find('WithNVs') >= 0:
    sx = test.replace('WithNVs', '')
    target_groups = ['NV', 'persistent', 'remission']
else:
    sx = test
    target_groups = ['persistent', 'remission']

for bidx, band in enumerate(bands):
    fname = '%s/%s_%d-%d_alwaysPositive_IC*_rtoz.nii' % (data_dir, subjs[0], band[0], band[1])
    ncomps = len(glob.glob(fname))
    for c in range(ncomps):
        data = np.zeros([len(subjs), nvoxels])
        data[:] = np.nan
        print 'Loading data: comp %d' % c, band
        for sidx, s in enumerate(subjs):
            # fname = '%s/%s_%d-%d_IC%02d.nii' % (data_dir, s, band[0],
            #                                     band[1], c)
            fname = '%s/%s_%d-%d_alwaysPositive_IC%02d_rtoz.nii' % (data_dir, s, band[0],
                                                          band[1], c)
            img = nb.load(fname)
            # subj_data = img.get_data()[:, :, :, 0]  # load beta coefficients
            # subj_data = img.get_data()[:, :, :, 2]  # load correlation
            subj_data = img.get_data()
            for v in range(nvoxels):
                data[sidx, v] = subj_data[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2])]
        print 'Running tests...'
        col_names = ['v%d' % i for i in range(nvoxels)]
        # uses the same index so we don't have issues concatenating later
        data_df = pd.DataFrame(data, columns=col_names, index=gf.index, dtype=float)
        df = pd.concat([gf, data_df], axis=1)

        # selecting just specific groups
        groups = gf.group.tolist()
        idx = [i for i, v in enumerate(groups) if v in target_groups]

        res = np.zeros(img.get_data().shape[:3] + tuple([4]))  # ttest and pval
        res[:] = np.nan
        for v in range(nvoxels):
            good_subjs = np.nonzero(~np.isnan(df['v%d' % v]))[0]
            keep = np.intersect1d(good_subjs, idx)
            est = smf.ols(formula='v%d ~ %s + age + gender' % (v, sx), data=df.iloc[keep]).fit()
            # convert from coefficient to beta
            beta = est.params[sx]
            cc = beta * np.std(df.iloc[keep][sx]) / np.std(df.iloc[keep]['v%d' % v])
            res[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), 0] = est.tvalues[sx]
            res[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), 1] = 1 - est.pvalues[sx]
            res[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), 2] = beta
            res[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), 3] = cc

        # net_mask = data_dir + '/results/binNetMask_%d-%d_IC%02d_p01BF.nii' % (band[0], band[1], c)
        net_mask = home + '/data/meg/sam_narrow_8mm/brain_mask_888.nii'
        img = nb.load(net_mask)
        net_res = res
        net_res[:, :, :, 1] = np.multiply(res[:, :, :, 1], img.get_data() > 0)
        nsig = np.nansum(res[:, :, :, 1] > .95)
        print 'Significant voxels: %d (%.2f)' % (nsig, float(nsig) / nvoxels)
        fname = '%s/results/%sAgeGender_%d-%d_IC%02d_rtoz.nii' % (data_dir, test, band[0], band[1], c)
        print 'Saving results to %s' % fname
        nb.save(nb.Nifti1Image(net_res, img.get_affine()), fname)
