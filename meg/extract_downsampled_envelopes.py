# Script to extract data per subject in a given band
# by Gustavo Sudre, October 2014
import numpy as np
import mne
import os
import sys
home = os.path.expanduser('~')
lib_path = os.path.abspath(home+'/research_code/meg/')
sys.path.append(lib_path)
import find_good_segments as fg
from scipy import stats

band = [65, 100]  # [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
window_length = 13.65  # sec
fifs_dir = home + '/data/meg/rest/'  # '/mnt/neuro/MEG_data/fifs/rest/'
out_dir = home + '/data/meg/sam_narrow_8mm/'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
markers_fname = home+'/data/meg/marker_data_clean.npy'
markers = np.load(markers_fname)[()]

# downsampled data is stored in a dictionary
all_data = {}
# For each subject, we use the weight matrix to compute virtual electrodes
for s in subjs:
    raw_fname = fifs_dir + '/%s_rest_LP100_CP3_DS300_raw.fif' % s
    raw = mne.io.Raw(raw_fname, preload=True, compensation=3)
    picks = mne.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    raw.filter(l_freq=band[0], h_freq=band[1], picks=picks)
    weights = np.load(out_dir + s + '_%d-%d_weights.npz' % (band[0], band[1]))['weights']
    data, time = raw[picks, :]
    # instead of getting the hilbert of the source space (costly), do the Hilbert first and compute the envelope later
    raw.apply_hilbert(picks, envelope=False)
    events = fg.get_good_events(markers[s], time, window_length)
    epochs = mne.Epochs(raw, events, None, 0, window_length, preload=True, baseline=None, detrend=0, picks=picks)
    # it will go faster to concatenate everything now, downsample it, and then multiply the weights
    epoch_data = epochs.get_data()
    epoch_data = epoch_data.swapaxes(1, 0)
    nchans, nreps, npoints = epoch_data.shape
    sensor_data = epoch_data.reshape([nchans, nreps*npoints])
    sensor_data = sensor_data[:, np.arange(0, nreps*npoints,
                                           int(raw.info['sfreq']))]
    # get the abs() of Hilbert transform (Hilbert envelope)
    sol = abs(np.dot(weights, sensor_data))

    all_data[s] = stats.mstats.zscore(sol, axis=1)

np.save(out_dir + '/downsampled_envelopes_%d-%d' % (band[0], band[1]),
        all_data)
