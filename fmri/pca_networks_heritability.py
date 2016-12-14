''' Spits out the first X PCs of networks to a CSV file '''

import numpy as np
import os
home = os.path.expanduser('~')
import nibabel as nb
from sklearn.decomposition import PCA
import glob


ncomps = 3
# subjs_fname = home + '/data/fmri_example11_all/elbow.txt'
# data_dir = home + '/data/fmri_example11_all/dual_elbow/'
mygroup = '3min'
subjs_fname = home + '/data/fmri_example11_all/%s.txt' % mygroup
data_dir = home + '/data/fmri_example11_all/melodic/%s/dual/' % mygroup
net_mask_dir = data_dir
out_fname = home + '/data/fmri_example11_all/fmri_melodicNoMaskZ_%s_%dcomps.csv' % (mygroup, ncomps)
save_comps = False
# subjs_fname = home + '/data/fmri_example11_all/famAndSibs.txt'
# data_dir = home + '/data/fmri_example11_all/dual/'
# net_mask_dir = home + '/data/fmri_example11_all/ica/'
# out_fname = home + '/data/fmri_example11_all/fmri_famAndSibs_%dcomps.csv' % ncomps
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

# just so we only open each subject's data once, let's construct a list
# where each item is the subject's data, voxels by IC
data = []
for s, subj in enumerate(subjs):
    print 'Loading subject %d / %d' % (s + 1, len(subjs))
    img = nb.load(data_dir + 'dr_stage2_%s_Z.nii.gz' % subj)
    # img = nb.load(data_dir + 'dr_stage2_%s.nii.gz' % subj)
    x, y, z, nics = img.get_data().shape
    nvoxels = x * y * z
    data.append(np.reshape(img.get_data(), [nvoxels, nics]))

# then, open each network mask, and run the PCA for only the voxels
# in each network
pcs = np.empty([len(subjs), ncomps * nics])
# the order is all pcs for net1, then all pcs for net2, etc
header = ['subj'] + ['net%02d_pc%02d' % (n, p) for n in range(nics)
                     for p in range(ncomps)]
cnt = 0
for n in range(nics):
    print 'Working on net %d / %d' % (n + 1, nics)
    # mask = nb.load(net_mask_dir + '/IC%d_binNetMask_p01a01.nii' % n)
    mask = nb.load(home + '/data/fmri_example11_all/brain_mask_555.nii')
    # mask = nb.load(net_mask_dir + '/IC%d_binNetMask_p01.nii' % (n + 1))
    # good voxels
    gv = mask.get_data().astype(bool).flatten()
    nvoxels = np.sum(gv)
    print nvoxels
    subj_data = np.zeros([len(subjs), nvoxels])
    subj_data[:] = np.nan
    for s in range(len(subjs)):
        subj_data[s, :] = data[s][gv, n]
    pca = PCA(n_components=ncomps)
    pcs[:, cnt:(cnt + ncomps)] = pca.fit_transform(subj_data)
    for c in range(ncomps):
        print '    comp %d, %.2f' % (c, pca.explained_variance_ratio_[c])
    cnt += ncomps

    if save_comps:
        weights = np.zeros([len(gv), ncomps])
        for i in range(ncomps):
            weights[gv, i] = pca.components_[i, :]
        weights = weights.reshape(mask.get_data().shape[:3] + tuple([-1]))
        nb.save(nb.Nifti1Image(weights, mask.get_affine()), net_mask_dir + '/IC%d_PCs.nii' % n)

# spitting it out to CSV
fid = open(out_fname, 'w')
fid.write(','.join(header) + '\n')
for r in range(pcs.shape[0]):
    fid.write('%s,' % subjs[r])
    fid.write(','.join(['%f' % d for d in pcs[r, :]]) + '\n')
fid.close()
