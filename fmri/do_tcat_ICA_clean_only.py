# Script to calculate ICA on fMRI data concatenated over time
# by Gustavo Sudre, July 2014
import numpy as np
import os
import sys
home = os.path.expanduser('~')
lib_path = os.path.abspath(home+'/research_code/meg/')
sys.path.append(lib_path)
from scipy import stats
from sklearn.decomposition import FastICA
# from sklearn.preprocessing import Imputer
import nibabel as nb


if len(sys.argv) > 1:
    nreal = int(sys.argv[1])
else:
    nreal = 1


ncomps = 30
data_dir = home + '/data/fmri/downsampled_444/'
subjs_fname = home + '/data/fmri/joel_all_ica2.txt'
res_dir = home + '/data/fmri/ica/'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

init_sources = 70000
init_time = 30400

# create huge array so we can add all the data and then resize it appropriately
print 'Creating big static matrix...'
all_data = np.empty([init_sources, init_time])
all_data[:] = np.nan
cnt = 0

print 'Concatenating subjects...'
mask = nb.load(data_dir + '/brain_mask_444.nii')
# good voxels
gv = mask.get_data().astype(bool).flatten()
nvoxels = np.sum(gv)
a = []
delme = []
for sidx, s in enumerate(subjs):
    print 'Subject %d / %d' % (sidx + 1, len(subjs))
    img = nb.load(data_dir + s + '.nii')
    data = img.get_data()
    img_dims = data.shape
    # data becomes voxels by time
    data = data.reshape([data.size / img_dims[-1], -1])
    data = data[gv, :]
    data = stats.mstats.zscore(data, axis=1)
    this_del = list(np.nonzero(np.isnan(np.sum(data, axis=1)))[0])
    delme += this_del
    a.append(len(this_del))
    all_data[0:nvoxels, cnt:(cnt + data.shape[1])] = data
    cnt += data.shape[1]
all_data = all_data[:nvoxels, :cnt]

# remove sources that have NaNs for at least one subject
delme = np.unique(delme)
all_data = np.delete(all_data, delme, axis=0)

# applying ICA and figuring out how each IC scores
print 'Applying FastICA, voxels: %d original, %d estimated, time: %d' % (nvoxels, all_data.shape[0], all_data.shape[1])

rng = np.random.RandomState()
ica = FastICA(n_components=ncomps, random_state=rng)
ICs = ica.fit_transform(all_data).T
fname = res_dir + 'catAllWithTopSubjs_R%02d.npz' % nreal
np.savez(fname, ICs=ICs, subjs=subjs, delme=delme)
