from __future__ import division
import numpy as np
from matplotlib import pylab

samplerate = 44100
N = 100000
time = 1. / samplerate * np.arange(N)
freq = samplerate / N * np.arange(N)
f1 = 750
a1 = 1.5
f2 = 4400
a2 = 4
y = a1 * np.sin(2 * np.pi * f1 * time) + a2 * np.sin(2 * np.pi *f2 * time)
h = np.fft.fft(y,n=1024)
pylab.plot(freq[:N // 2], np.abs(h[:N // 2]))
pylab.show()
normalization = 2 / N
h = np.fft.fft(y)
pylab.plot(freq[:N // 2], normalization * np.abs(h[:N // 2]))
pylab.show()