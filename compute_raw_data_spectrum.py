"""
==================================================
Compute the power spectral density of raw data
==================================================

This script shows how to compute the power spectral density (PSD)
of measurements on a raw dataset. Based on the example code in the MNE website.

"""
# Authors: Gustavo Sudre, 01/2013

import numpy as np

from mne import fiff
from mne.time_frequency import compute_raw_psd

from spreadsheet import get_subjects_from_excel

###############################################################################
# Set parameters
data_path = '/Users/sudregp/MEG_data/fifs/'
tmin, tmax = 10, 130  # use the first 2min of data after the first 10s
fmin, fmax = 1, 228  # look at frequencies between 1 and 228
NFFT = 2048  # the FFT size (NFFT). Ideally a power of 2

subjs = get_subjects_from_excel()

# let's do one subject to get the dimensions
subj = subjs.keys()[0]
raw_fname = data_path + subj + '_rest_LP100_HP0.6_CP3_DS300_raw.fif'
raw = fiff.Raw(raw_fname)
picks = fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
tmp, freqs = compute_raw_psd(raw, tmin=tmin, tmax=tmax, picks=picks,
        fmin=fmin, fmax=fmax, NFFT=NFFT, n_jobs=1,
        plot=False, proj=False)
psds = np.zeros_like(np.tile(tmp, [len(subjs), 1, 1]))

# Loop through all the subjects we find. Calculate the power in all channels
for idx, subj in enumerate(subjs):
    raw_fname = data_path + subj + '_rest_LP100_HP0.6_CP3_DS300_raw.fif'

    # Setup for reading the raw data
    raw = fiff.Raw(raw_fname)

    psds[idx], freqs = compute_raw_psd(raw, tmin=tmin, tmax=tmax, picks=picks,
        fmin=fmin, fmax=fmax, NFFT=NFFT, n_jobs=1,
        plot=False, proj=False)

# Creating labels based on ADHD diagnostic
adhd = np.zeros(len(subjs), dtype=bool)
for idx, subj in enumerate(subjs):
    if subjs[subj].find('ADHD') >= 0 or subjs[subj].find('proband') >= 0:
        adhd[idx] = True
    elif subjs[subj].find('NV') >= 0 or subjs[subj].find('unaffected') >= 0:
        adhd[idx] = False
    else:
        print "Don't know status of subject " + subj

np.savez('../MEG_data/analysis/rest/good_PSDS', psds=psds, subjs=subjs, adhd=adhd, info=raw.info, freqs=freqs, picks=picks)
