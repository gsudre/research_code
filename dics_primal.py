from mne.time_frequency.tfr import cwt_morlet
import numpy as np
from scipy import linalg
from mne import fiff
import mne

raw_fname = '/Users/sudregp/mne-python/examples/MNE-sample-data/MEG/sample/sample_audvis_filt-0-40_raw.fif'
fname_fwd = '/Users/sudregp/mne-python/examples/MNE-sample-data/MEG/sample/sample_audvis-meg-oct-6-fwd.fif'
chans = range(306)
freqs = [10, 20, 30]
reg = 0.001
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
Y = Y[:,:N // 2]
# Yamp = normalization * np.abs(h[:N // 2]))

# Y is chans x freqs. First, keep only the frequencies we're interested in.
keep_freqs = []
for f in freqs:
    # find the first occurrence of the frequency of interest
    keep_freqs.append(np.nonzero(freq.astype(int)==f)[0][0])

Y = Y[:,keep_freqs]

# probably don't need to compute it for all channels, nor save all the values!
Cxy = np.zeros([len(chans), len(chans), len(freqs)], dtype=complex)
for idx in enumerate(chans):
    for jdx in enumerate(chans):
        Cxy[idx, jdx, :] =  Y[idx, :] * np.conj(Y[jdx, :])

forward = mne.read_forward_solution(fname_fwd)
# APPLY SSP VECTORS?
# ONLY DO IT FOR GOOD CHANNELS!

# only select the tangential dipoles

L = forward['sol']['data'][:,]
for idx, freq in enumerate(freqs):
    C = np.squeeze(Cxy[:,:,idx])
    U, s, V = np.linalg.svd(C)
    Cr = C + reg * s[0] * np.eye(forward['sol']['nrow'])
    A = np.dot(L.T, np.linalg.inv(C), L)


