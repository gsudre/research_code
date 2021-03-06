import mne
import numpy as np
import find_good_segments as fg
import copy as cp
from os.path import expanduser

data_reg = .001
noise_reg = .03
method=['pli','imcoh','plv','wpli','pli2_unbiased','wpli2_debiased']
label_mode = 'pca_flip'
home = expanduser('~')
data_dir = '/mnt/neuro/MEG_data/'
dir_out = home+'/data/meg/connectivity/Yeo-Hillebrand/'
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

labels = mne.labels_from_parc('fsaverage', parc='Yeo2011_7Networks_N1000')[0]
net_labels = labels[:-2] # the last two are the medial wall
# fill them in so we can morph them later
for label in net_labels:
    label.values.fill(1.0)
labels = mne.labels_from_parc('fsaverage', parc='aparc')[0]
# because the labels represent the whole network, I'll need to compute connecitvity among all sources within the label, instead of extracting one time course per label. But that turned out to be a HUGE matrix, so let's identify the intersection of aparc labels and Yeo labels, and just use those. But we need to compute the intersection using fsaverage, to make sure every subject has the same number of labels.
avg_intersects = []
for net in net_labels:
    label_intersect = []
    for l in labels:
        verts_in_both = np.intersect1d(l.vertices, net.vertices)
        if len(verts_in_both)>0:
            label_intersect.append(mne.Label(vertices=verts_in_both, hemi=net.hemi, subject=net.subject, name=net.name))
    avg_intersects.append(label_intersect)

for subj in subjs[95:115]:
    er_fname = empty_room_dir+'empty_room_'+closest_empty_room[subj]+'_raw.fif'
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

    epochs = mne.Epochs(raw, events, None, 0, window_length, preload=True, baseline=None, detrend=0, picks=picks)
    stcs = mne.beamformer.lcmv_epochs(epochs, forward, noise_cov.as_diag(), data_cov, reg=data_reg, pick_ori='max-power')

    for net in avg_intersects:
        subj_labels = [label.morph('fsaverage',subj) for label in net]
        label_ts = mne.extract_label_time_course(stcs, subj_labels, forward['src'], mode=label_mode, allow_empty=True)
        con, freqs, times, n_epochs, n_tapers = mne.connectivity.spectral_connectivity(label_ts, method=method, mode='multitaper', sfreq=raw.info['sfreq'], fmin=[1,4,8,13,30], fmax=[4,8,13,30,50], faverage=True, n_jobs=3, mt_adaptive=False)
        np.save(dir_out + subj + '-' + net[0].name + '-' + label_mode +'-' + '-'.join(method), con)