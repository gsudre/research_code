# Script to generate conectivity in SAM narrow band
# by Gustavo Sudre, July 2014
import numpy as np
import mne
import os, sys
home = os.path.expanduser('~')
lib_path = os.path.abspath(home+'/research_code/meg/')
sys.path.append(lib_path)
import find_good_segments as fg


bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
window_length=13.65  #s
fifs_dir = '/mnt/neuro/MEG_data/fifs/rest/'
out_dir = home + '/data/meg/sam_narrow/'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
markers_fname = home+'/data/meg/marker_data_clean.npy'
markers = np.load(markers_fname)[()]        
method=['pli','imcoh','plv','wpli','pli2_unbiased','wpli2_debiased']

# For each subject, we use the weight matrix to compute virtual electrodes
for s in subjs:
    raw_fname = fifs_dir + '/%s_rest_LP100_CP3_DS300_raw.fif'%s
    raw = mne.fiff.Raw(raw_fname, preload=True, compensation=3)
    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    conn = []
    for band in bands:
        band_raw = raw.copy()
        band_raw.filter(l_freq=band[0],h_freq=band[1],picks=picks)
        weights = np.load(out_dir + s + '_%d-%d_weights.npz'%(band[0],band[1]))['weights']
        data, time = band_raw[picks, :]
        events = fg.get_good_events(markers[s], time, window_length)
        epochs = mne.Epochs(raw, events, None, 0, window_length, preload=True, baseline=None, detrend=0, picks=picks)
        sols = [np.dot(weights, epoch) for epoch in epochs]
        band_conn = mne.connectivity.spectral_connectivity(sols, method=method, mode='multitaper', sfreq=300, fmin=band[0], fmax=band[1], faverage=True, n_jobs=1, mt_adaptive=False)[0]
        conn.append(band_conn)
    np.save(out_dir + s + '_roi_connectivity', conn)
