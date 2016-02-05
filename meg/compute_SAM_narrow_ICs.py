# Script to calculate ICA on SAM narrow bands
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


ncomps = 30
nreals = 60
res_dir = home + '/tmp/'
band = [65, 100]  # [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
fifs_dir = home + '/data/meg/rest/'
out_dir = home + '/data/meg/sam_narrow_8mm/'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
group_fname = subjs_fname  # home + '/data/meg/nv_subjs.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

init_sources = 20500
init_time = 38500

# create huge array so we can add all the data and then resize it appropriately
print 'Creating big static matrix...'
all_data = np.empty([init_sources, init_time])
all_data[:] = np.nan
cnt = 0

# open the saved files with the downsampled data
print 'Loading data...', band
ds_data = np.load(out_dir + '/downsampled_envelopes_%d-%d.npy' % (band[0],
                                                                  band[1]))[()]

print 'Concatenating subjects...'
fid = open(group_fname, 'r')
subj_group = [line.rstrip() for line in fid]
fid.close()
nsources = ds_data.values()[0].shape[0]
# For each subject, we use the weight matrix to compute virtual electrodes
for s in subjs:
    if s in subj_group:
        subj_data = ds_data[s]
        all_data[0:nsources, cnt:(cnt + subj_data.shape[1])] = subj_data
        cnt += subj_data.shape[1]
all_data = all_data[:nsources, :cnt]

# remove sources that have NaNs for at least one subject
delme = np.nonzero(np.isnan(np.sum(all_data, axis=1)))[0]
all_data = np.delete(all_data, delme, axis=0)

# applying ICA and figuring out how each IC scores
print 'Applying FastICA, sources: %d original, %d estimated, time: %d' % (nsources, all_data.shape[0], all_data.shape[1])

# rng = np.random.RandomState()
# for i in range(nreals):
#     print 'Realization %d of %d' % (i+1, nreals)
#     ica = FastICA(n_components=ncomps, random_state=rng)
#     ICs = ica.fit_transform(all_data.T).T
#     fname = res_dir + 'catNVSubjs_%d-%d' % (band[0], band[1]) + '_R%02d.npz' % (i + 1)
#     np.savez(fname, ICs=ICs)
