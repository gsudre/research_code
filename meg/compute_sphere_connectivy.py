# Script to extract sphere data per subject in a given band and calculate
# connectivity using MNE
# by Gustavo Sudre
import numpy as np
import mne
import os
import sys
import find_good_segments as fg


home = os.path.expanduser('~')
lib_path = os.path.abspath(home + '/research_code/meg/')
sys.path.append(lib_path)

s = sys.argv[1]  # 'AKMNQNHX'
method = sys.argv[2]
bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
window_length = 13.65  # sec
fifs_dir = home + '/data/meg/rest/'  # '/mnt/neuro/MEG_data/fifs/rest/'
weights_dir = home + '/data/meg/sam_narrow_8mm/'
out_dir = home + '/data/meg/rois_spheres/'
vox_fname = home + '/data/fmri_full_grid/rois_spheres/' + \
                   'spheresIdxInYeo_888r4.txt'
fid = open(vox_fname, 'r')
vox = np.array([int(line.rstrip()) for line in fid])
fid.close()
markers_fname = home + '/data/meg/marker_data_clean.npy'
markers = np.load(markers_fname)[()]

# correlation matrices stored here
all_data = {}
# For each subject, we use the weight matrix to compute virtual electrodes
for band in bands:
    print band
    # reload the data because we re-filter it every time
    raw_fname = fifs_dir + '/%s_rest_LP100_CP3_DS300_raw.fif' % s
    raw = mne.io.Raw(raw_fname, preload=True, compensation=3)
    picks = mne.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    weights = np.load(weights_dir + s +
                      '_%d-%d_weights.npz' % (band[0], band[1]))['weights']
    # remove sources not in fMRI
    weights = weights[vox, :]
    data, time = raw[picks, :]
    events = fg.get_good_events(markers[s], time, window_length)
    epochs = mne.Epochs(raw, events, None, 0, window_length, preload=True,
                        baseline=None, detrend=0, picks=picks)

    epoch_data = epochs.get_data()
    nepochs, nsensors, ntimes = epoch_data.shape
    epoch_data = epoch_data.swapaxes(1, 0)
    sensor_data = np.resize(epoch_data, [epoch_data.shape[0], -1])
    print 'Localizing sources'
    sol = abs(np.dot(weights, sensor_data))

    # source_data = np.resize(sol, [sol.shape[0], nepochs, ntimes])
    # source_data = source_data.swapaxes(1, 0)

    # MNE expect nepochs as the first dimension
    source_data = sol[np.newaxis, :]
    con = mne.connectivity.spectral_connectivity(source_data, method=method,
                                                 sfreq=epochs.info['sfreq'],
                                                 mode='multitaper',
                                                 fmin=band[0],
                                                 fmax=band[1],
                                                 faverage=True)[0]
    con = con.squeeze()

    bname = '%d-%d' % (band[0], band[1])
    all_data[bname] = con

print 'Saving results'
np.save(out_dir + '/%s_%s.npy' % (s, method), all_data)
