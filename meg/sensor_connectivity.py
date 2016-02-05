import mne
import numpy as np
import find_good_segments as fg
from os.path import expanduser

method=['pli','imcoh','plv','wpli','pli2_unbiased','wpli2_debiased']
home = expanduser('~')
data_dir = '/mnt/neuro/MEG_data/'
dir_out = home+'/data/meg/connectivity/sensor/'
window_length=13.65  #s

subjs_fname = home+'/data/meg/usable_subjects_5segs13p654.txt'
markers_fname = home+'/data/meg/marker_data_clean.npy'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]

markers = np.load(markers_fname)[()]

for subj in subjs[59:63]:
    raw_fname = data_dir + 'fifs/rest/%s_rest_LP100_CP3_DS300_raw.fif'%subj
    raw = mne.fiff.Raw(raw_fname, preload=True, compensation=3)
    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    raw.filter(l_freq=1, h_freq=50, picks=picks)
    data, time = raw[picks, :]
    events = fg.get_good_events(markers[subj], time, window_length)

    epochs = mne.Epochs(raw, events, None, 0, window_length, preload=True, baseline=None, detrend=0, picks=picks)

    con, freqs, times, n_epochs, n_tapers = mne.connectivity.spectral_connectivity(epochs, method=method, mode='multitaper', sfreq=raw.info['sfreq'], fmin=[1,4,8,13,30], fmax=[4,8,13,30,50], faverage=True, n_jobs=1, mt_adaptive=False)
    np.save(dir_out + subj + '-sensor-' + '-'.join(method), con)