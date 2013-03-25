from matplotlib import mlab
import numpy as np
from mne.parallel import parallel_func


def compute_psd(signals, Fs, NFFT=2048, fmin=0, fmax=np.inf, n_jobs=1):
    """Based on the code in compute_raw_psd"""
    NFFT = int(NFFT)
    print "Effective window size : %0.3f (s)" % (NFFT / float(Fs))

    if n_jobs > 1:
        parallel, my_psd, n_jobs = parallel_func(mlab.psd, n_jobs)
        out = parallel(my_psd(d, Fs=Fs, NFFT=NFFT) for d in signals)
        freqs = out[0][1]
        psd = np.array(zip(*out)[0])
    else:
        parallel, my_psd, n_jobs = parallel_func(mlab.psd, n_jobs)
        psd = []
        for d in signals:
            p, freqs = mlab.psd(d, Fs=Fs, NFFT=NFFT)
            psd.append(p)
        psd = np.array(p)

    mask = (freqs >= fmin) & (freqs <= fmax)
    freqs = freqs[mask]
    psd = psd[:, mask]

    return psd, freqs
