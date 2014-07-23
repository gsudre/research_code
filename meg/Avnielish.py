import mne
import numpy as np
import find_good_segments as fg
import copy as cp
from os.path import expanduser

snr = 3.0  
lambda2 = 1.0 / snr ** 2
noise_reg=.03
method=['pli','imcoh','plv','wpli','pli2_unbiased','wpli2_debiased']
label_mode = 'mean_flip'
home = expanduser('~')
data_dir = '/mnt/neuro/MEG_data/'
dir_out = home+'/data/meg/connectivity/MNE/'
empty_room_dir = '/mnt/neuro/MEG_data/empty_room/'
# empty_room_dir = '/Users/sudregp/data/meg_empty_room/'
res = np.recfromtxt(empty_room_dir + 'closest_empty_room_data.csv',skip_header=0,delimiter=',')
window_length=13.65  #s
closest_empty_room = {}
for rec in res:
    closest_empty_room[rec[0]] = str(rec[2])

subjs_fname = home+'/data/meg/usable_subjects_5segs13p654.txt'
markers_fname = home+'/data/meg/marker_data_clean.npy'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]

markers = np.load(markers_fname)[()]

for subj in subjs:
    er_fname = empty_room_dir+'empty_room_'+closest_empty_room[subj]+'_raw.fif'
    raw_fname = data_dir + 'fifs/rest/%s_rest_LP100_CP3_DS300_raw.fif'%subj
    fwd_fname = data_dir + 'analysis/rest/%s_rest_LP100_CP3_DS300_raw-5-fwd.fif'%subj
    forward = mne.read_forward_solution(fwd_fname, surf_ori=True)
    raw = mne.fiff.Raw(raw_fname, preload=True, compensation=3)
    er_raw = mne.fiff.Raw(er_fname, preload=True, compensation=3)
    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    raw.filter(l_freq=1, h_freq=50, picks=picks)
    er_raw.filter(l_freq=1, h_freq=50, picks=picks)

    noise_cov = mne.compute_raw_data_covariance(er_raw)
    # note that MNE reads CTF data as magnetometers!
    noise_cov = mne.cov.regularize(noise_cov, raw.info, mag=noise_reg)
    inverse_operator = mne.minimum_norm.make_inverse_operator(raw.info, forward, noise_cov, loose=0.2, depth=0.8)
    data, time = raw[0,:] #
    events = fg.get_good_events(markers[subj], time, window_length)

    epochs = mne.Epochs(raw, events, None, 0, window_length, preload=True, baseline=None, detrend=0, picks=picks)
    stcs = mne.minimum_norm.apply_inverse_epochs(epochs, inverse_operator, lambda2, 'MNE',return_generator=False)

    labels, label_colors = mne.labels_from_parc(subj, parc='aparc')
    label_ts = mne.extract_label_time_course(stcs, labels, forward['src'], mode=label_mode)

    # label_data is nlabels by time, so here we can use whatever connectivity method we fancy
    con, freqs, times, n_epochs, n_tapers = mne.connectivity.spectral_connectivity(label_ts, method=method, mode='multitaper', sfreq=raw.info['sfreq'], fmin=[1,4,8,13,30], fmax=[4,8,13,30,50], faverage=True, n_jobs=3, mt_adaptive=False)
    np.save(dir_out + subj + '-' + label_mode +'-' + '-'.join(method), con)