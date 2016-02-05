''' Checks how much variability the PCs of a network explains '''

import numpy as np
import os
home = os.path.expanduser('~')
import nibabel as nb
from sklearn.decomposition import PCA


z_thresh = [0, 1.5, 2, 3, 4, 5]  # tries different masks
comps = [0, 1, 2, 3, 5, 6, 9, 10, 11, 12, 14, 16, 17, 18, 19, 21, 22, 25]
pca_comps = 5
subjs_fname = home+'/data/fmri/joel_all.txt'
data_dir = home + '/data/fmri/ica/dual_regression_AllSubjsZeroFilled/'
ic_fname = home + '/data/fmri/ica/catAllSubjsZeroFilled_aligned_corr0.80_alwaysPositive_avgICmap_zscore.nii'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

mask = nb.load(home + '/data/fmri/downsampled_444/brain_mask_444.nii')
# good voxels
gv = mask.get_data().astype(bool).flatten()
nvoxels = np.sum(gv)

for comp in comps:
    data = np.zeros([len(subjs), nvoxels])
    data[:] = np.nan
    print 'Loading data: comp %d' % comp
    for s, subj in enumerate(subjs):
        img = nb.load(data_dir + 'dr_stage2_%s.nii.gz' % subj)
        subj_data = img.get_data()[:, :, :, comp].flatten()
        data[s, :] = subj_data[gv]
    # load the z-scored network map
    img = nb.load(ic_fname)
    ic_data = img.get_data()[:, :, :, comp].flatten()[gv]
    # for each threshold, check how much variance is explained by 1st IC
    for z in z_thresh:
        idx = ic_data > z
        X = data[:, idx]
        pca = PCA(n_components=pca_comps)
        pca.fit(X)
        print('Z=%.2f, voxels=%d, variance=' % (z, np.sum(idx)) +
              str(pca.explained_variance_ratio_) + ' total=%.2f' % np.sum(pca.explained_variance_ratio_))
