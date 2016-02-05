# generate several STC files for the task data to later run voxel-wise stats

import mne
from mne.minimum_norm import apply_inverse, make_inverse_operator
from mne.beamformer import lcmv
from mne.time_frequency import compute_epochs_csd
from mne.beamformer import dics, dics_source_power
import sys
import numpy as np


if len(sys.argv) > 1:
    subj = sys.argv[1]
else:
    subj = 'BIPRUXZS'

conds = ['STI-correct', 'STI-incorrect']
out_dir = '/mnt/shaw/MEG_data/analysis/stop/source_surface_at_red/'
fwd_dir = '/mnt/shaw/MEG_data/analysis/stop/'
data_dir = '/mnt/shaw/MEG_data/analysis/stop/parsed_red/'
snr = 3.0
lambda2 = 1.0 / snr ** 2
method = "dSPM"  # use dSPM method (could also be MNE or sLORETA)
bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
btmin = -.5
btmax = -.0001
tmin = 0
tmax = .5

# read in the epoched, averaged, and forward solution
fname_fwd = fwd_dir + '%s_task-5-fwd.fif' % subj
forward = mne.read_forward_solution(fname_fwd)
evoked_fname = data_dir + '%s_stop_parsed_matched_clean_BP1-100_DS300-ave.fif' % subj
evoked = mne.read_evokeds(evoked_fname)
epochs_fname = data_dir + '%s_stop_parsed_matched_clean_BP1-100_DS300-epo.fif.gz' % subj
epochs = mne.read_epochs(epochs_fname)

# we're interested in time points every 50ms (for now). That's sfreq of 20Hz.
# the niquist there is 10Hz, so let's downsample our data that way.
epochs_ds = epochs.copy()
epochs_ds.resample(20)
evoked_ds = [epochs_ds[name].average() for name in ['STI-correct', 'STI-incorrect']]

# contruct two types of inverse solution: one based on baseline data (before the red square appears), and one based on blank data
cov_blank = mne.compute_covariance(epochs_ds['STB'], tmin=0, tmax=None, method='auto')
inv_blank = make_inverse_operator(epochs_ds.info, forward, cov_blank,
                                  loose=0.2, depth=0.8)
blank_idx = np.nonzero(epochs_ds.events[:, 2] == 15)[0]
epochs_ds.drop_epochs(blank_idx)
cov_base = mne.compute_covariance(epochs_ds, tmin=None, tmax=0, method='auto')
inv_base = make_inverse_operator(epochs_ds.info, forward, cov_base,
                                 loose=0.2, depth=0.8)

vertices_to = [np.arange(10242), np.arange(10242)]
vertices_from = [forward['src'][0]['vertno'], forward['src'][1]['vertno']]
morph_mat = mne.compute_morph_matrix(subj, 'fsaverage', vertices_from, vertices_to)
for c in range(len(conds)):
    # start with the simplest method, MNE + dSPM
    stc = apply_inverse(evoked_ds[c], inv_base, lambda2, method)
    stc = mne.morph_data_precomputed(subj, 'fsaverage', stc,
                                     vertices_to, morph_mat)
    fname = out_dir + '%s_%s_dSPM_base_clean' % (subj, conds[c])
    stc.save(fname)
    stc = apply_inverse(evoked_ds[c], inv_blank, lambda2, method)
    stc = mne.morph_data_precomputed(subj, 'fsaverage', stc,
                                     vertices_to, morph_mat)
    fname = out_dir + '%s_%s_dSPM_blank_clean' % (subj, conds[c])
    stc.save(fname)

    # the next estimate is LCMV beamformer in time
    data_cov = mne.compute_covariance(epochs_ds[conds[c]], tmin=0, tmax=None,
                                      method='shrunk')
    stc = lcmv(evoked_ds[c], forward, cov_blank, data_cov, reg=0.01,
               pick_ori='max-power')
    stc = mne.morph_data_precomputed(subj, 'fsaverage', stc,
                                     vertices_to, morph_mat)
    fname = out_dir + '%s_%s_LCMV_blank_clean' % (subj, conds[c])
    stc.save(fname)
    stc = lcmv(evoked_ds[c], forward, cov_base, data_cov, reg=0.01,
               pick_ori='max-power')
    stc = mne.morph_data_precomputed(subj, 'fsaverage', stc,
                                     vertices_to, morph_mat)
    fname = out_dir + '%s_%s_LCMV_base_clean' % (subj, conds[c])
    stc.save(fname)

    # finally, compute DICS per band
    for band in bands:
        data_csd = compute_epochs_csd(epochs[conds[c]], mode='multitaper',
                                      tmin=tmin, tmax=tmax + btmax,
                                      fmin=band[0], fmax=band[1])
        noise_csd = compute_epochs_csd(epochs[conds[c]], mode='multitaper',
                                       tmin=btmin, tmax=btmax,
                                       fmin=band[0], fmax=band[1])
        stc = dics(evoked[c], forward, noise_csd, data_csd)
        stc = mne.morph_data_precomputed(subj, 'fsaverage', stc,
                                         vertices_to, morph_mat)
        stc.resample(20)
        fname = out_dir + '%s_%s_DICSevoked_%dto%d_clean' % (subj, conds[c],
                                                       band[0], band[1])
        stc.save(fname)
        stc = dics_source_power(epochs.info, forward, noise_csd, data_csd)
        stc = mne.morph_data_precomputed(subj, 'fsaverage', stc,
                                         vertices_to, morph_mat)
        fname = out_dir + '%s_%s_DICSepochs_%dto%d_clean' % (subj, conds[c],
                                                       band[0], band[1])
        stc.save(fname)
