
import os
home = os.path.expanduser('~')
import numpy as np
import nibabel as nb
from scipy import stats


data_dir = home + '/data/fmri/ica/dual_regression_AllSubjsZeroFilled/'
out_dir = home + '/data/fmri/ica/'
ic = 15
subjs_fname = home+'/data/fmri/joel_all.txt'
group_fname = home+'/data/fmri/joel_nvs.txt'
group_fname = home+'/data/fmri/joel_remission.txt'
group_fname = home+'/data/fmri/joel_persistent.txt'

mask = nb.load(home + '/data/fmri/downsampled_444/brain_mask_444.nii')
# good voxels
gv = mask.get_data().astype(bool)
nvoxels = len(gv)
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
fid = open(group_fname, 'r')
group = [line.rstrip() for line in fid]
fid.close()

cnt = 0
subj_data = np.zeros(mask.get_data().shape)
for s, subj in enumerate(subjs):
    if subj in group:
        img = nb.load(data_dir + 'dr_stage2_%s.nii.gz' % subj)
        subj_data += img.get_data()[:, :, :, ic].squeeze()
        cnt += 1
subj_data /= cnt

zs = stats.zscore(subj_data[gv])
z = np.zeros(subj_data.shape)
z[gv] = zs

fname = group_fname.split('/')[-1].split('.')[0].split('_')[-1]
nb.save(nb.Nifti1Image(subj_data, mask.get_affine()), out_dir + fname + '_ic%02d.nii' % ic)
nb.save(nb.Nifti1Image(z.reshape(mask.get_data().shape), mask.get_affine()), out_dir + fname + '_ic%02d_zs.nii' % ic)
