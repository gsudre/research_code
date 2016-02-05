''' Spits out the first X PCs of networks to a CSV file '''

import numpy as np
import os
home = os.path.expanduser('~')
import nibabel as nb
from sklearn.decomposition import PCA
import pylab as pl


subjs_fname = home + '/data/fmri_example11_all/melodic/3min.txt'
data_dir = home + '/data/fmri_example11_all/melodic/3min/dual/'
net_mask_dir = data_dir
# ics = [15, 8, 11, 23, 7, 2, 17]  # 2min
# ics = [13, 4, 7, 21, 10, 16, 19]  # 3min
# ics = [24, 7, 4, 22, 10, 11, 19]  # 4min
# ics = [12, 11, 1, 14, 10, 21, 16]  # elbow
ics = [13, 8, 0, 22, 1, 24, 16]  # 2min
ics = [16, 8, 0, 25, 11, 24, 13]  # 3min
ics = [14, 4, 5, 23, 18, 9, 12]  # 4min
ics = [2, 21, 17, 13, 16, 24, 14]  # elbow
ics = [3, 6, 12, 5, 13, 7, 1, 9]  # 3min, melodicMasked
ic_names = ['visual', 'somatomotor', 'dorsal', 'ventral',
            'limbic', 'frontoparietal', 'default', 'default2']

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

# just so we only open each subject's data once, let's construct a list
# where each item is the subject's data, voxels by IC
data = []
for s, subj in enumerate(subjs):
    print 'Loading subject %d / %d' % (s + 1, len(subjs))
    subj = subj[3:-4]
    img = nb.load(data_dir + 'dr_stage2_%s_Z.nii.gz' % subj)
    x, y, z, nics = img.get_data().shape
    nvoxels = x * y * z
    data.append(np.reshape(img.get_data(), [nvoxels, nics]))

pl.figure()
cnt = 1
for n in ics:
    # mask = nb.load(net_mask_dir + '/IC%d_binNetMask_p01a01.nii' % n)
    mask = nb.load(net_mask_dir + '/IC%d_binNetMask_p01.nii' % n)
    # good voxels
    gv = mask.get_data().astype(bool).flatten()
    nvoxels = np.sum(gv)
    print nvoxels
    subj_data = np.zeros([len(subjs), nvoxels])
    subj_data[:] = np.nan
    for s in range(len(subjs)):
        subj_data[s, :] = data[s][gv, n]
    pca = PCA()
    pca.fit_transform(subj_data)
    pl.subplot(2, 4, cnt)
    pl.plot(pca.explained_variance_ratio_)
    pl.title('IC %d: %s' % (n, ic_names[cnt - 1]), fontsize='small')
    pl.xlim([0, 10])
    cnt += 1
pl.tight_layout()
