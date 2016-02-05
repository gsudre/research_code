
import os
home = os.path.expanduser('~')
import numpy as np
import nibabel as nb
from scipy import stats
import sys

if len(sys.argv) > 1:
    subj = sys.argv[1]
    freq_band = None
    res_dir = home + '/data/results/graicar/fmri/'
else:
    # subj = 'JOAOCEOG'
    # freq_band = '8-13'
    # res_dir = home + '/data/results/graicar/meg/'
    subj = 'subj2'
    freq_band = None
    res_dir = home + '/data/results/graicar/fmri/'

ICs = np.load(res_dir + subj + '_aligned.npz')['average_ICs']

mask = nb.load(home + '/Downloads/demo/group/mask/grpmask.nii.gz')
# good voxels
gv = mask.get_data().astype(bool).flatten()

ncomps = len(ICs)
nvoxels = np.sum(gv)

avg_ICs = np.zeros([gv.shape[0], ncomps])
z_ICs = np.zeros([gv.shape[0], ncomps])
# for each aligned IC
for i in range(ncomps):
    avg_ICs[gv, i] = ICs[i, :]
    z_ICs[gv, i] = stats.mstats.zscore(ICs[i, :])

avg_ICs = avg_ICs.reshape(mask.get_data().shape[:3] + tuple([-1]))
fname = res_dir + subj + '_avgICmap.nii'
nb.save(nb.Nifti1Image(avg_ICs, mask.get_affine()), fname)

z_ICs = z_ICs.reshape(mask.get_data().shape[:3] + tuple([-1]))
fname = res_dir + subj + '_avgICmap_zscore.nii'
nb.save(nb.Nifti1Image(z_ICs, mask.get_affine()), fname)
