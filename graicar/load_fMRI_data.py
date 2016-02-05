
import os
home = os.path.expanduser('~')
from scipy import stats
import nibabel as nb

data_dir = home + '/data/fmri/downsampled_444/%s.nii'
print 'Loading data for', subj
img = nb.load(data_dir % subj)
mask = nb.load(home + '/data/fmri/downsampled_444/brain_mask_444.nii')
data = img.get_data()
# good voxels
gv = mask.get_data().astype(bool).flatten()
img_dims = data.shape
# data becomes voxels by time
data = data.reshape([data.size / img_dims[-1], -1])
data = data[gv, :]
data = stats.mstats.zscore(data, axis=0)

# transpose the matrix so we can use the same code to generate ICs
data = data.T
