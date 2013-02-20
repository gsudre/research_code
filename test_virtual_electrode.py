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

label_names = ['Aud-lh', 'Aud-rh']
labels = [mne.read_label(data_path + '/MEG/sample/labels/%s.label' % ln)
          for ln in label_names]

###############################################################################
# Generate source time courses and the correspond evoked data
snr = 1  # dB
tmin = 0
tstep = 1. / raw.info['sfreq']
ntimes = 2000

# Generate times series from 2 Morlet wavelets
stc_data = np.zeros((len(labels), ntimes))
Ws = morlet(raw.info['sfreq'], [3, 10], n_cycles=[1, 1.5])
stc_data[0][:len(Ws[0])] = np.real(Ws[0])
stc_data[1][:len(Ws[1])] = np.real(Ws[1])
stc_data *= 100 * 1e-9  # use nAm as unit

# time translation
stc_data[1] = np.roll(stc_data[1], 80)
stc = generate_sparse_stc(fwd['src'], labels, stc_data, tmin, tstep)

###############################################################################
# Generate noisy evoked data
picks = mne.fiff.pick_types(raw.info, meg=True)
iir_filter = iir_filter_raw(raw, order=5, picks=picks, tmin=60, tmax=180)
evoked = generate_evoked(fwd, stc, evoked_template, cov, snr, iir_filter=iir_filter)
raw[:306,:ntimes] = evoked.data
raw = raw.crop(tmax=evoked.times[-1])
raw.save('t2-raw.fif')

raw2 = mne.fiff.Raw('t2-raw.fif')
cov = mne.compute_raw_data_covariance(raw2)


weights = ve.calculate_weights(fwd, cov, reg=0)

d, _ = raw2[:306,:]
sol = np.dot(weights, d)
src = mne.SourceEstimate(sol, (fwd['src'][0]['vertno'], fwd['src'][1]['vertno']), tmin, tstep)


# plotting the localized source
const = 2*10**-10
good_data = np.nonzero(abs(src.data[:,150])>const)
lv = np.nonzero(abs(src.lh_data[:,150])>const)
rv = np.nonzero(abs(src.rh_data[:,150])>const)
src.data = np.squeeze(src.data[np.ix_(good_data[0]),:])
src.vertno = [np.array([src.lh_vertno[lv[0][0]]]), np.array([src.rh_vertno[rv[0][0]]])]

# plotting the simulated source
plot_sparse_source_estimates(fwd['src'], stc, bgcolor=(1, 1, 1), opacity=0.5, high_resolution=True)