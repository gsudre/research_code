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
    subj = 'ABUTRIKQ'

conds = ['STI-correct', 'STI-incorrect']
out_dir = '/mnt/shaw/MEG_data/analysis/stop/source_volume_at_cross/'
fwd_dir = '/mnt/shaw/MEG_data/analysis/stop/'
data_dir = '/mnt/shaw/MEG_data/analysis/stop/parsed/'
subjs_dir = '/mnt/shaw/MEG_structural/freesurfer/'
snr = 3.0
lambda2 = 1.0 / snr ** 2
method = "dSPM"  # use dSPM method (could also be MNE or sLORETA)
bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
btmin = -.5
btmax = -.0001
tmin = 0
tmax = .5

# read in the epoched, averaged, and forward solution
fname_fwd = fwd_dir + '%s_task-vol-5-fwd.fif' % subj
forward = mne.read_forward_solution(fname_fwd)
# epochs_fname = data_dir + '%s_stop_parsed_matched_clean_BP1-100_DS300-epo.fif.gz' % subj
epochs_fname = data_dir + '%s_stop_parsed_matched_clean_BP1-100_DS300-epo.fif.gz' % subj
epochs = mne.read_epochs(epochs_fname)

# we're interested in time points every 50ms (for now). That's sfreq of 20Hz.
# the niquist there is 10Hz, so let's downsample our data that way.
epochs_ds = epochs.copy()
epochs_ds.resample(20)
evoked_ds = [epochs_ds[name].average() for name in conds]
evoked = [epochs[name].average() for name in conds]

# contruct two types of inverse solution: one based on baseline data (before the red square appears), and one based on blank data
cov_blank = mne.compute_covariance(epochs_ds['STB'], tmin=0, tmax=None, method='auto')
# sometimes we cannot create the inverse
try:
    inv_blank = make_inverse_operator(epochs_ds.info, forward, cov_blank,
                                      loose=0.2, depth=0.8)
except:
    inv_blank = None
blank_idx = np.nonzero(epochs_ds.events[:, 2] == 15)[0]
epochs_ds.drop_epochs(blank_idx)
cov_base = mne.compute_covariance(epochs_ds, tmin=None, tmax=0, method='auto')
try:
    inv_base = make_inverse_operator(epochs_ds.info, forward, cov_base,
                                     loose=0.2, depth=0.8)
except:
    inv_base = None

for c in range(len(conds)):
    # start with the simplest method, MNE + dSPM
    if inv_base is not None:
        stc = apply_inverse(evoked_ds[c], inv_base, lambda2, method)
        fname = out_dir + '%s_%s_dSPM_base_clean' % (subj, conds[c])
        stc.save(fname)
    if inv_blank is not None:
        stc = apply_inverse(evoked_ds[c], inv_blank, lambda2, method)
        fname = out_dir + '%s_%s_dSPM_blank_clean' % (subj, conds[c])
        stc.save(fname)

    # the next estimate is LCMV beamformer in time
    data_cov = mne.compute_covariance(epochs_ds[conds[c]], tmin=0, tmax=None,
                                      method='auto')
    stc = lcmv(evoked_ds[c], forward, cov_blank, data_cov, reg=0.01,
               pick_ori='max-power')
    fname = out_dir + '%s_%s_LCMV_blank_clean' % (subj, conds[c])
    stc.save(fname)
    stc = lcmv(evoked_ds[c], forward, cov_base, data_cov, reg=0.01,
               pick_ori='max-power')
    fname = out_dir + '%s_%s_LCMV_base_clean' % (subj, conds[c])
    stc.save(fname)

    # finally, compute DICS per band
    for band in bands:
        # DICSevoked does DICS over time
        data_csd = compute_epochs_csd(epochs[conds[c]], mode='multitaper',
                                      tmin=tmin, tmax=tmax + btmax,
                                      fmin=band[0], fmax=band[1])
        noise_csd = compute_epochs_csd(epochs[conds[c]], mode='multitaper',
                                       tmin=btmin, tmax=btmax,
                                       fmin=band[0], fmax=band[1])
        stc = dics(evoked[c], forward, noise_csd, data_csd)
        stc.resample(20)
        fname = out_dir + '%s_%s_DICSevoked_%dto%d_clean' % (subj, conds[c],
                                                             band[0], band[1])
        stc.save(fname)

        # DICSepochs has one value per band for the total time window
        stc = dics_source_power(epochs.info, forward, noise_csd, data_csd)
        fname = out_dir + '%s_%s_DICSepochs_%dto%d_clean' % (subj, conds[c],
                                                             band[0], band[1])
        stc.save(fname)

print 'Computing difference in conditions:'

methods = ['LCMV_base', 'LCMV_blank',
           'DICSepochs_1to4', 'DICSepochs_4to8', 'DICSepochs_8to13', 'DICSepochs_13to30', 'DICSepochs_30to55', 'DICSepochs_65to100',
           'DICSevoked_1to4', 'DICSevoked_4to8', 'DICSevoked_8to13', 'DICSevoked_13to30', 'DICSevoked_30to55', 'DICSevoked_65to100']
if inv_base is not None:
    methods.append('dSPM_base')
if inv_blank is not None:
    methods.append('dSPM_blank')
for m in methods:
    stcc = mne.read_source_estimate('%s/%s_STI-correct_%s_clean-vl.stc' % (out_dir, subj, m))
    stci = mne.read_source_estimate('%s/%s_STI-incorrect_%s_clean-vl.stc' % (out_dir, subj, m))
    stc = stcc - stci
    stc.save('%s/%s_correctVSincorrect_%s_clean' % (out_dir, subj, m))
