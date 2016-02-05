
import os
home = os.path.expanduser('~')
import numpy as np
import nibabel as nb
from scipy import stats

# res_dir = home + '/data/heritability_fmri/ica/all/'
res_dir = home + '/data/fmri_example11_all/ica/'
# fname = res_dir + 'catAllZeroFilled_aligned_corr0.70'
fname = res_dir + 'catFamAndSibsElbowZeroFilled_aligned_corr0.80'
ICs = np.load(fname + '.npz')['average_ICs']
delme = np.load(fname + '.npz')['delme']

# mask = nb.load(home + '/data/heritability_fmri/brain_mask_444.nii')
mask = nb.load(home + '/data/fmri_example11_all/brain_mask_555.nii')
# good voxels
gv = mask.get_data().astype(bool).flatten()
nvoxels = len(gv)

ncomps = len(ICs)

avg_ICs = np.zeros([nvoxels, ncomps])
z_ICs = np.zeros([nvoxels, ncomps])

if delme[()] is not None:
    gv = np.delete(np.nonzero(gv)[0], delme, axis=0)
else:
    gv = np.nonzero(gv)[0]

# for each aligned IC
for i in range(ncomps):
    z = stats.mstats.zscore(ICs[i, :])
    tmp = np.argmax(np.abs(z))
    if np.sign(z[tmp]) > 0:
        avg_ICs[gv, i] = ICs[i, :]
        z_ICs[gv, i] = z
    else:
        avg_ICs[gv, i] = -ICs[i, :]
        z_ICs[gv, i] = -z

avg_ICs = avg_ICs.reshape(mask.get_data().shape[:3] + tuple([-1]))
nb.save(nb.Nifti1Image(avg_ICs, mask.get_affine()), fname + '_alwaysPositive_avgICmap.nii')

z_ICs = z_ICs.reshape(mask.get_data().shape[:3] + tuple([-1]))
nb.save(nb.Nifti1Image(z_ICs, mask.get_affine()), fname + '_alwaysPositive_avgICmap_zscore.nii')
