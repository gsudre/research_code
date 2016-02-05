''' Spits out the correlation of the mean activity over many clusters in a network. It only does it for networks with more than one cluster, and we also keep track of the different connection names, so that we can use the same in proc.tcl'''

import numpy as np
import os
home = os.path.expanduser('~')
import nibabel as nb
import glob


subjs_fname = home + '/data/fmri_example11_all/2min.txt'
data_dir = home + '/data/fmri_example11_all/'
net_mask_dir = home + '/data/fmri_example11_all/dual_2min/'
out_fname = home + '/data/fmri_example11_all/fmri_2min_corr.csv'

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

# then, open each cluster mask, and take the correlation of average
# activity in each cluster
masks = glob.glob(net_mask_dir + '/clusts_IC*_binNetMask_p01a01.nii')
nics = len(masks)

corrs = []
# for each subject
for s in range(len(subjs)):
    print 'Working on subject %d / %d' % (s + 1, len(subjs))
    subj_corrs = []
    conn_names = []
    for n in range(nics):
        mask = nb.load(net_mask_dir + '/clusts_IC%d_binNetMask_p01a01.nii' % n)
        nclust = len(np.unique(mask.get_data())) - 1  # remove 0
        if nclust > 1:
            # create a matrix of signal by cluster
            subj_means = []
            for c in np.unique(mask.get_data())[1:]:
                # good voxels
                gv = mask.get_data() == c
                subj_means.append(np.mean(data[s][gv.flatten(), :],
                                          axis=0))
            idx = np.triu_indices(nclust, k=1)
            val = np.corrcoef(subj_means)[idx]
            subj_corrs.append([d for d in val])
            conn_names.append(['net%d_%dto%d' % (n, idx[0][i], idx[1][i])
                               for i in range(len(idx[0]))])
    # flattening
    corrs.append([i for j in subj_corrs for i in j])
conn_names = [i for j in conn_names for i in j]

corrs = np.array(corrs)
header = ['subj'] + ['conn%02d' % n for n in range(corrs.shape[1])]

# spitting it out to CSV
fid = open(out_fname, 'w')
fid.write(','.join(header) + '\n')
for r in range(corrs.shape[0]):
    fid.write('%s,' % subjs[r])
    fid.write(','.join(['%f' % d for d in corrs[r, :]]) + '\n')
fid.close()

# also spit out the name of each connections
fid = open(out_fname[:-4] + '_map.csv', 'w')
for n in range(corrs.shape[1]):
    fid.write('conn%02d = %s\n' % (n, conn_names[n]))
fid.close()
