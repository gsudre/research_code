"""
==================================================
Compute the power spectral density of raw data
==================================================

This script shows how to compute the power spectral density (PSD)
of measurements on a raw dataset. Based on the example code in the MNE website.

"""
# Authors: Gustavo Sudre

import numpy as np

from mne import fiff, read_proj, read_selection
from mne.time_frequency import compute_raw_psd

###############################################################################
# Set parameters
data_path = '/Users/sudregp/Documents/20110909/'
raw_fname = data_path + 'rest.fif'

# Setup for reading the raw data
raw = fiff.Raw(raw_fname)

tmin, tmax = 10, 130  # use the first 2min of data after the first 10s
fmin, fmax = 1, 228  # look at frequencies between 1 and 228
NFFT = 2048  # the FFT size (NFFT). Ideally a power of 2
psds, freqs = compute_raw_psd(raw, tmin=tmin, tmax=tmax,
                              fmin=fmin, fmax=fmax, NFFT=NFFT, n_jobs=1,
                              plot=False, proj=False)


# Convert PSDs to dB
psds = 10 * np.log10(psds)  

###############################################################################
# Compute mean and standard deviation accross channels and then plot
def plot_psds(freqs, psds, fill_color):
    psd_mean = np.mean(psds, axis=0)
    psd_std = np.std(psds, axis=0)
    hyp_limits = (psd_mean - psd_std, psd_mean + psd_std)

    pl.plot(freqs, psd_mean)
    pl.fill_between(freqs, hyp_limits[0], y2=hyp_limits[1], color=fill_color,
                    alpha=0.5)

import pylab as pl
pl.figure()
plot_psds(freqs, psds, (0, 0, 1, .3))
pl.xlabel('Freq (Hz)')
pl.ylabel('Power Spectral Density (dB/Hz)')
pl.legend(['Without SSP'])
pl.show()

