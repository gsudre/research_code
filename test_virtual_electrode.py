"""
==============================
Testing if virtual electrode is working
==============================

"""
# Author: Gustavo Sudre, heavily borrowed from the version on the MNE website from 
# Daniel Strohmeier <daniel.strohmeier@tu-ilmenau.de>
#         Alexandre Gramfort <gramfort@nmr.mgh.harvard.edu>
#
# License: BSD (3-clause)

import numpy as np
import pylab as pl

import mne
from mne.fiff.pick import pick_types_evoked, pick_types_forward
from mne.datasets import sample
from mne.time_frequency import iir_filter_raw, morlet
from mne.viz import plot_evoked, plot_sparse_source_estimates
from mne.simulation import generate_sparse_stc, generate_evoked
import virtual_electrode as ve

###############################################################################
# Load real data as templates
data_path = sample.data_path('/Users/sudregp/mne-python/examples/')

raw = mne.fiff.Raw(data_path + '/MEG/sample/sample_audvis_raw.fif', preload=True)

fwd_fname = data_path + '/MEG/sample/sample_audvis-meg-eeg-oct-6-fwd.fif'
ave_fname = data_path + '/MEG/sample/sample_audvis-no-filter-ave.fif'
cov_fname = data_path + '/MEG/sample/sample_audvis-cov.fif'

fwd = mne.read_forward_solution(fwd_fname, force_fixed=True, surf_ori=True)
fwd = pick_types_forward(fwd, meg=True)

cov = mne.read_cov(cov_fname)

evoked_template = mne.fiff.read_evoked(ave_fname, setno=0, baseline=None)

label_names = ['Aud-lh', 'Aud-lh', 'Aud-lh', 'Aud-lh', 'Aud-lh']
labels = [mne.read_label(data_path + '/MEG/sample/labels/%s.label' % ln)
          for ln in label_names]

###############################################################################
# Generate source time courses and the correspond evoked data
snr = 1  # dB
tmin = 0
tstep = 1. / raw.info['sfreq']
# ntimes = 2000

# let's create 2 sources with the same frequency in lh, but one with more power than the other. in rh, we'll create two sources with different frequencies
Fs = raw.info['sfreq']
Ts = 1.0/Fs; # sampling interval
t = np.arange(0,4,Ts) # time vector
# bands = ([.5, 4], [4, 8], [8, 13], [13, 30], [30, 58])
bands = [[8, 13], [13, 30], [30, 58]]
ff = [23, 11, 23, 47, 23];   # frequency of the signal
stc_data = np.zeros((len(labels), len(t)))
for idy, y in enumerate(ff):
    stc_data[idy, :] = np.sin(2*np.pi*y*t)
stc_data[0,:] *= 1000
stc_data[2,:] *= 100
stc_data[4,:] *= 10
stc_data[2] = np.roll(stc_data[2], 80)
stc_data[4] = np.roll(stc_data[4], 90)
ntimes = len(t)

'''
# Generate times series from 2 Morlet wavelets
stc_data = np.zeros((len(labels), ntimes))
Ws = morlet(raw.info['sfreq'], [3, 10, 20, 40], n_cycles=[1, 1.5, 2, 2.5])
stc_data[0][:len(Ws[0])] = np.real(Ws[0])
stc_data[1][:len(Ws[1])] = np.real(Ws[1])
stc_data[2][:len(Ws[2])] = np.real(Ws[2])
stc_data[3][:len(Ws[3])] = np.real(Ws[3])
stc_data += 100 * 1e-9  # use nAm as unit

# time translation
stc_data[1] = np.roll(stc_data[1], 80)
'''

stc = generate_sparse_stc(fwd['src'], labels, stc_data, tmin, tstep)

###############################################################################
# Generate noisy evoked data
picks = mne.fiff.pick_types(raw.info, meg=True)
iir_filter = iir_filter_raw(raw, order=5, picks=picks, tmin=60, tmax=180)
evoked = generate_evoked(fwd, stc, evoked_template, cov, snr) #, iir_filter=iir_filter)
raw[:306,:ntimes] = evoked.data
raw = raw.crop(tmax=evoked.times[-1])
raw.save('t2-raw.fif')

raw2 = mne.fiff.Raw('t2-raw.fif')
cov = mne.compute_raw_data_covariance(raw2)

dsim = stc.in_label(labels[0])
pl.plot(dsim.data.T)

weights = ve.calculate_weights(fwd, cov, reg=0)

d, _ = raw2[:306,:]
sol = np.dot(weights, d)
src = mne.SourceEstimate(sol, (fwd['src'][0]['vertno'], fwd['src'][1]['vertno']), tmin, tstep)

'''
# plotting the localized source
const = 1*10**-18
good_data = np.nonzero(abs(src.data[:,150])>const)
lv = np.nonzero(abs(src.lh_data[:,150])>const)
rv = np.nonzero(abs(src.rh_data[:,150])>const)
src.data = np.squeeze(src.data[np.ix_(good_data[0]),:])
src.vertno = [np.array([src.lh_vertno[lv[0][0]]]), np.array([src.rh_vertno[rv[0][0]]])]

# plotting the simulated source
plot_sparse_source_estimates(fwd['src'], stc, bgcolor=(1, 1, 1), opacity=0.5, high_resolution=True)
'''

selected_voxels = ve.find_best_voxels(src, labels, bands)
num_trials = 5
num_samples = 100
label_activity = np.zeros([num_trials, len(labels), num_samples])
pli = []
for band in np.arange(len(bands)):
    label_ts = np.zeros((len(labels), ntimes))
    for idl, label in enumerate(labels):
        label_signal = src.in_label(label)
        label_ts[idl, :] = label_signal.data[selected_voxels[idl, band], :]
        # here we pick 5 artifact-free trials with 4096 samples (about 13s in the original paper) and use that as trials
        for trial in np.arange(num_trials):
            label_activity[trial, idl, :] = label_ts[idl, trial:trial + num_samples]
    con = mne.connectivity.spectral_connectivity(label_activity,
        method='pli', mode='multitaper', sfreq=Fs, fmin=bands[band][0], fmax=bands[band][1], faverage=True, mt_adaptive=True, n_jobs=2)
    pli.append(con)
