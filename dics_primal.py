from mne.time_frequency.tfr import cwt_morlet
import numpy as np
from mne import fiff

raw_fname = '/Users/sudregp/mne-python/examples/MNE-sample-data/MEG/sample/sample_audvis_filt-0-40_raw.fif'
chans = range(5)
freqs = [10, 20, 30]

raw = fiff.Raw(raw_fname)

frequencies = np.arange(6, 20, 5)  # define frequencies of interest
Fs = raw.info['sfreq']  # sampling in Hz
n_cycles = frequencies / float(4)

data, times = raw[:, :]

N = len(times)
dt = 1. / raw.info['sfreq']
Y = np.fft.fft(data)
freq = np.fft.fftfreq(N, d=dt)
normalization = 2. / N
freq = freq[:N // 2]
Y = Y[,:N // 2]
# Yamp = normalization * np.abs(h[:N // 2]))

# Y is chans x freqs. First, keep only the frequencies we're interested in.
keep_freqs = []
for f in freqs:
    # find the first occurrence of the frequency of interest
    keep_freqs.append(nonzero(freq.astype(int)==f)[0][0])

Y = Y[:,keep_freqs]

# probably don't need to compute it for all channels, nor save all the values!
Cxy = zeros([len(chans), len(chans), len(freqs)])
for idx in enumerate(chans):
    for jdx in enumerate(chans):
        for f in enumerate(freqs):
            # CHECK THAT THIS IS WORKING!!! GOT A WEIRD WARNING... CHECK AGAINST THE MATLAB CODE... CAN WE RUN THE MATLAB CODE AND COMPARE OUTPUTS????
            Cxy[idx, jdx, :] =  multiply(Y[idx, :], Y[jdx, :].conj())
