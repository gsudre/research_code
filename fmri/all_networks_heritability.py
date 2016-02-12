''' Spits out every voxel in the brain mask to a CSV file '''

import numpy as np
import os
import nibabel as nb
home = os.path.expanduser('~')

# subjs_fname = home + '/data/fmri_example11_all/elbow.txt'
# data_dir = home + '/data/fmri_example11_all/dual_elbow/'
mydir = home + '/data/fmri_example11_all/'
mygroup = '3min'
subjs_fname = mydir + '/%s.txt' % mygroup
data_dir = mydir + '/melodic/%s/dual/' % mygroup
net_mask_dir = data_dir

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
nsubjs = len(subjs)

# just so we only open each subject's data once, let's construct a list
# where each item is the subject's data, voxels by IC
data = []
for s, subj in enumerate(subjs):
    print 'Loading subject %d / %d' % (s + 1, nsubjs)
    img = nb.load(data_dir + 'dr_stage2_%s_Z.nii.gz' % subj)
    x, y, z, nics = img.get_data().shape
    nvoxels = x * y * z
    data.append(np.reshape(img.get_data(), [nvoxels, nics]))

# the order is all pcs for net1, then all pcs for net2, etc
for n in range(nics):
    print 'Working on net %d / %d' % (n + 1, nics)
    mask = nb.load(mydir + '/brain_mask_555.nii')

    # good voxels
    gv = mask.get_data().astype(bool).flatten()
    nvoxels = np.sum(gv)
    header = ['subj'] + ['v%d' % (v + 1) for v in range(nvoxels)]
    print nvoxels
    subj_data = np.zeros([len(subjs), nvoxels])
    subj_data[:] = np.nan
    for s in range(nsubjs):
        subj_data[s, :] = data[s][gv, n]

    out_fname = mydir + '/fmri_melodicMasked_%s_net%02d.csv' % (mygroup, n)
    # spitting it out to CSV
    fid = open(out_fname, 'w')
    fid.write(','.join(header) + '\n')
    for r in range(nsubjs):
        fid.write('%s,' % subjs[r])
        fid.write(','.join(['%f' % d for d in subj_data[r, :]]) + '\n')
    fid.close()
