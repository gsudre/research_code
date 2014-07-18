import mne
import numpy as np
import find_good_segments as fg
import copy as cp

data_reg = .001
noise_reg = .03
method='pli'
data_dir = '/mnt/neuro/MEG_data/'
dir_out = '/Users/sudregp/data/meg_diagNoise_segments/connectivity/'
empty_room_dir = '/Users/sudregp/data/meg_empty_room/'
res = np.recfromtxt(empty_room_dir + 'closest_empty_room_data.csv',skip_header=0,delimiter=',')
window_length=13.654  #s
closest_empty_room = {}
subjs = []
for rec in res:
    closest_empty_room[rec[0]] = str(rec[2])
    subjs.append(rec[0])

subjs_fname = '/Users/sudregp/data/meg/usable_subjects_5segs13p654.txt'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]

markers = np.load('/Users/sudregp/data/meg/marker_data_clean.npy')[()]

for subj in subjs:
    er_fname = empty_room_dir+'empty_room_'+closest_empty_room[subj]+'.fif'
    raw_fname = data_dir + 'fifs/rest/%s_rest_LP100_CP3_DS300_raw.fif'%subj
    fwd_fname = data_dir + 'analysis/rest/%s_rest_LP100_CP3_DS300_raw-5-fwd.fif'%subj
    forward = mne.read_forward_solution(fwd_fname, surf_ori=True)
    raw = mne.fiff.Raw(raw_fname, preload=True, compensation=3)
    er_raw = mne.fiff.Raw(er_fname, preload=True, compensation=3)
    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    raw.filter(l_freq=1, h_freq=50, picks=picks)
    er_raw.filter(l_freq=1, h_freq=50, picks=picks)

    # we need to exclude the bad segments first before computing the raw data covariance, but MNE doesn't let us do that within the function. So, I just copied their code for computing raw data covariance below, and adapted to my needs (from cov.py)
    data, time = raw[picks, :]
    idx = fg.get_good_indexes(markers[subj], time)
    raw_data = data[:, idx]
    start = 0
    stop = len(idx)
    step = int(np.ceil(.2 * raw.info['sfreq']))
    data = 0
    n_samples = 0
    mu = 0
    for first in range(start, stop, step):
        last = first + step
        if last >= stop:
            last = stop
        raw_segment = raw_data[:, first:last]
        mu += raw_segment.sum(axis=1)
        data += np.dot(raw_segment, raw_segment.T)
        n_samples += raw_segment.shape[1]
    mu /= n_samples
    data -= n_samples * mu[:, None] * mu[None, :]
    data /= (n_samples - 1.0)
    ch_names = [raw.info['ch_names'][k] for k in picks]
    data_cov = mne.Covariance(None)
    data_cov.update(kind=mne.fiff.FIFF.FIFFV_MNE_NOISE_COV, diag=False, 
        dim=len(data), names=ch_names, data=data, 
        projs=cp.deepcopy(raw.info['projs']), bads=raw.info['bads'], 
        nfree=n_samples, eig=None, eigvec=None)

    noise_cov = mne.compute_raw_data_covariance(er_raw)
    # note that MNE reads CTF data as magnetometers!
    noise_cov = mne.cov.regularize(noise_cov, raw.info, mag=noise_reg)
    events = fg.get_good_events(markers[subj], time, window_length)

    # WE'LL NEED TO CHOOSE HOW MANY EPOCHS TO USE. LET'S START WITH ALL OF THEM TO GET THE BEST ESTIMATE POSSIBLE, BUT WE'LL NEED TO VERIFY THAT IN THE FUTURE

    epochs = mne.Epochs(raw, events, None, 0, window_length, preload=True, baseline=None, detrend=0, picks=picks)
    stcs = mne.beamformer.lcmv_epochs(epochs, forward, noise_cov.as_diag(), data_cov, reg=data_reg, pick_ori='max-power')

    labels, label_colors = mne.labels_from_parc(subj, parc='aparc')
    label_ts = mne.extract_label_time_course(stcs, labels, forward['src'], mode='mean_flip')

    # label_data is nlabels by time, so here we can use whatever connectivity method we fancy
    con, freqs, times, n_epochs, n_tapers = mne.connectivity.spectral_connectivity(label_ts, method=method, mode='multitaper', sfreq=raw.info['sfreq'], fmin=[1,4,8,13,30], fmax=[4,8,13,30,50], faverage=True, n_jobs=2, mt_adaptive=False)
    np.save(dir_out + method + '-' + subj, con)