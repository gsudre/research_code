
import os
home = os.path.expanduser('~')
import numpy as np
import nibabel as nb
from scipy import stats

res_dir = home + '/data/results/graicar/fmri/'
aligned_ICs = np.load(res_dir + 'group_aligned.npz')['aligned_ICs']
rep_mats = np.load(res_dir + 'group_aligned.npz')['rep_mats']
subjs = np.load(res_dir + 'group_aligned.npz')['subjs']
loadings = np.load(res_dir + 'group_aligned.npz')['loadings']

# mask = nb.load(home + '/Downloads/demo/group/mask/grpmask.nii.gz')
mask = nb.load(home + '/tmp/mask_group.nii')
# good voxels
gv = mask.get_data().astype(bool).flatten()

ncomps = len(aligned_ICs)
nvoxels = np.sum(gv)

avg_ICs = np.zeros([gv.shape[0], ncomps])
z_ICs = np.zeros([gv.shape[0], ncomps])
# for each aligned IC
for i in range(ncomps):
    # construct the averaged IC over subjects
    avg_ic = np.zeros(nvoxels)
    for s in range(len(subjs)):
        sid = aligned_ICs[i][s][0]
        fname = res_dir + '%s_aligned.npz' % (subjs[sid])
        my_ic = np.load(fname)['average_ICs'][aligned_ICs[i][s][1], :]
        my_ic = stats.mstats.zscore(my_ic)
        if s > 0:
            cc = np.corrcoef(my_ic, avg_ic)[0, 1]
        else:
            cc = 1
        avg_ic += np.sign(cc) * loadings[i][sid] * my_ic
    avg_ic /= len(subjs)
    avg_ICs[gv, i] = avg_ic
    z_ICs[gv, i] = stats.mstats.zscore(avg_ic)

avg_ICs = avg_ICs.reshape(mask.get_data().shape[:3] + tuple([-1]))
fname = res_dir + 'subjectAlignedICs.nii'
nb.save(nb.Nifti1Image(avg_ICs, mask.get_affine()), fname)

z_ICs = z_ICs.reshape(mask.get_data().shape[:3] + tuple([-1]))
fname = res_dir + 'subjectAlignedICs_zscore.nii'
nb.save(nb.Nifti1Image(z_ICs, mask.get_affine()), fname)
