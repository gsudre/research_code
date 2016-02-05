''' Spits out the mean over network masks to a CSV file '''

import numpy as np
import os
home = os.path.expanduser('~')
import nibabel as nb
import glob


subjs_fname = home + '/data/fmri_example11_all/2min.txt'
data_dir = home + '/data/fmri_example11_all/'
net_mask_dir = home + '/data/fmri_example11_all/dual_2min/'
out_fname = home + '/data/fmri_example11_all/fmri_2min_mean.csv'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

# just so we only open each subject's data once, let's construct a list
# where each item is the subject's data, voxels by IC
data = []
for s, subj in enumerate(subjs):
    print 'Loading subject %d / %d' % (s + 1, len(subjs))
    img = nb.load(data_dir + '%s.nii' % subj)
    x, y, z, trs = img.get_data().shape
    nvoxels = x * y * z
    data.append(np.reshape(img.get_data(), [nvoxels, trs]))

# then, open each network mask, and take the mean of only the voxels
# in each network
masks = glob.glob(net_mask_dir + '/IC*_binNetMask_p01a01.nii')
nics = len(masks)

means = np.empty([len(subjs), nics])
# the order is all pcs for net1, then all pcs for net2, etc
header = ['subj'] + ['net%02d' % n for n in range(nics)]

for n in range(nics):
    print 'Working on net %d / %d' % (n + 1, nics)
    mask = nb.load(net_mask_dir + '/IC%d_binNetMask_p01a01.nii' % n)
    # good voxels
    gv = mask.get_data().astype(bool).flatten()
    for s in range(len(subjs)):
        means[s, n] = np.mean(data[s][gv, :])

# spitting it out to CSV
fid = open(out_fname, 'w')
fid.write(','.join(header) + '\n')
for r in range(means.shape[0]):
    fid.write('%s,' % subjs[r])
    fid.write(','.join(['%f' % d for d in means[r, :]]) + '\n')
fid.close()
