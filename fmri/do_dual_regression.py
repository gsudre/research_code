# Script to calculate ICA on fMRI data concatenated over time
# by Gustavo Sudre, July 2014
import numpy as np
import os
import sys
home = os.path.expanduser('~')
lib_path = os.path.abspath(home+'/research_code/meg/')
sys.path.append(lib_path)
from scipy import stats
import nibabel as nb


data_dir = home + '/data/heritability_fmri/'
subjs_fname = home + '/data/heritability_fmri/family_and_sibs.txt'
res_dir = home + '/data/heritability_fmri/ica/family_and_sibs/'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

ICs = np.load(res_dir + 'catFamilyAndSibsZeroFilled_aligned_corr0.70.npz')['average_ICs']
ncomps = len(ICs)

mask = nb.load(data_dir + '/brain_mask_444.nii')
# good voxels
gv = mask.get_data().astype(bool).flatten()
nvoxels = np.sum(gv)
for sidx, s in enumerate(subjs):
    print 'Subject %d / %d' % (sidx + 1, len(subjs))
    img = nb.load(data_dir + s + '.nii')
    data = img.get_data()
    img_dims = data.shape
    # data becomes voxels by time
    data = data.reshape([data.size / img_dims[-1], -1])
    data = data[gv, :]
    ic_ts = np.linalg.lstsq(ICs.T, data)[0]
    ic_ts = stats.mstats.zscore(ic_ts, axis=1)
    subj_map = np.linalg.lstsq(ic_ts.T, data.T)[0]
    for ic in range(ncomps):
        d = np.zeros([gv.shape[0], 1])
        d[gv, 0] = subj_map[ic, :]
        d = d.reshape(mask.get_data().shape[:3] + tuple([-1]))
        fname = res_dir + s + '_IC%02d.nii' % ic
        nb.save(nb.Nifti1Image(d, mask.get_affine()), fname)
