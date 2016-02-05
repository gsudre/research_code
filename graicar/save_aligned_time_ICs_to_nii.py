
import os
import sys
home = os.path.expanduser('~')
import mne
import numpy as np
from scipy import stats
lib_path = os.path.abspath(home+'/research_code/meg/')
sys.path.append(lib_path)
import find_good_segments as fg
import nibabel as nb


# we need the raw MEG data AND the ICs. The trick is how much we can keep in memory. Let's try to keep all the MEG data and the weights, and load the ICs as necessayr. We also only produce the virtual electrodes we need
data_dir = home + '/data/meg/fifs/rest/'
weights_dir = home + '/data/meg/sam_narrow_8mm/'
markers_fname = home+'/data/meg/marker_data_clean.npy'
nwindow = 13.65
freq_band = '8-13'
res_dir = home + '/tmp/'  # /data/results/graicar/meg/'

subjs = np.load(res_dir + 'group_' + freq_band + '_aligned.npz')['subjs']
sensor_data = {}
weights = {}
for subj in subjs:
    raw = mne.io.Raw(data_dir + subj + '_rest_LP100_CP3_DS300_raw.fif', preload=True, compensation=3)
    picks = mne.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    band = [int(i) for i in freq_band.split('-')]
    raw.filter(l_freq=band[0], h_freq=band[1], picks=picks)
    weights[subj] = np.load(weights_dir + subj + '_' + freq_band + '_weights.npz')['weights']
    data, time = raw[picks, :]
    raw.apply_hilbert(picks, envelope=False)
    markers = np.load(markers_fname)[()]
    events = fg.get_good_events(markers[subj], time, nwindow)
    epochs = mne.Epochs(raw, events, None, 0, nwindow, preload=True, baseline=None, detrend=0, picks=picks)
    epoch_data = epochs.get_data()
    epoch_data = epoch_data.swapaxes(1, 0)
    nchans, nreps, npoints = epoch_data.shape
    sensor_data[subj] = epoch_data.reshape([nchans, nreps*npoints])

aligned_ICs = np.load(res_dir + 'group_' + freq_band + '_aligned.npz')['aligned_ICs']
rep_mats = np.load(res_dir + 'group_' + freq_band + '_aligned.npz')['rep_mats']

nvoxels = 10 # weights.values()[0].shape[0]
ncomps = 5 #len(aligned_ICs)
corr_ICs = np.empty([nvoxels, ncomps])
corr_ICs[:] = np.nan
# for each aligned IC
for i in range(ncomps):
    # construct the concatenated IC time series across subjects
    cat_ic = []
    mult = np.nanmean(rep_mats[i], axis=0)
    for s in range(len(subjs)):
        sid = aligned_ICs[i][s][0]
        fname = res_dir + '%s_%s_aligned.npz' % (subjs[sid], freq_band)
        my_ic = np.load(fname)['average_ICs'][aligned_ICs[i][s][1], :]
        cat_ic += list(mult[sid] * my_ic)
    # for each voxel
    for v in range(nvoxels):
        print i, v
        # construct the concatenated raw time series across subjects
        cat_raw = []
        for s in subjs:
            cat_raw += list(abs(np.dot(weights[s][v, :], sensor_data[s])))
        # record the correlation between IC and raw time series
        corr_ICs[v, i] = stats.pearsonr(cat_ic, cat_raw)[0]

# output correlation map to nii
vox_pos = np.genfromtxt(home + '/data/meg/sam_narrow_8mm/voxelsInBrain888.txt', delimiter=' ')
img = nb.load(home + '/data/TT_N27_888.nii')
# The i,j,k in data/meg/sam_narrow_5mm/voxelsInBrain.txt is the same as the i,j,k in the matrix returned by get_data(), so there is no need for masks.
d = np.zeros(img.get_data().shape + tuple([ncomps]))
for v in range(nvoxels):
    d[int(vox_pos[v, 0]), int(vox_pos[v, 1]), int(vox_pos[v, 2]), :] = corr_ICs[v, :]
fname = res_dir + 'subjectAlignedICs' + '_' + freq_band + '.nii'
nb.save(nb.Nifti1Image(d, img.get_affine()), fname)
