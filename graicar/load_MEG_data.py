
import os
import sys
home = os.path.expanduser('~')
import mne
import numpy as np
from scipy import stats
lib_path = os.path.abspath(home + '/research_code/meg/')
sys.path.append(lib_path)
import find_good_segments as fg

data_dir = home + '/data/meg/fifs/rest/'
# data_dir = home + '/tmp/'
weights_dir = home + '/data/meg/sam_narrow_8mm/'
markers_fname = home + '/data/meg/marker_data_clean.npy'
nwindow = 13.65

print data_dir

raw = mne.io.Raw(data_dir + subj + '_rest_LP100_CP3_DS300_raw.fif', preload=True, compensation=3)
picks = mne.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
band = [int(i) for i in freq_band.split('-')]
raw.filter(l_freq=band[0], h_freq=band[1], picks=picks)
weights = np.load(weights_dir + subj + '_' + freq_band + '_weights.npz')['weights']
data, time = raw[picks, :]
raw.apply_hilbert(picks, envelope=False)
markers = np.load(markers_fname)[()]
events = fg.get_good_events(markers[subj], time, nwindow)
epochs = mne.Epochs(raw, events, None, 0, nwindow, preload=True, baseline=None, detrend=0, picks=picks)
epoch_data = epochs.get_data()
epoch_data = epoch_data.swapaxes(1, 0)
nchans, nreps, npoints = epoch_data.shape
sensor_data = epoch_data.reshape([nchans, nreps*npoints])
# good voxels that are do not have weight zero
gv = np.nonzero(np.sum(weights, axis=1) != 0)[0]
ngv = gv.shape[0]
print 'Multiplying data by weights'
sol = abs(np.dot(weights[gv, :], sensor_data))
data = stats.mstats.zscore(sol, axis=1)
