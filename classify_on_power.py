"""

Classifies between ADHD and NV based on band power

"""
# Authors: Gustavo Sudre, 01/2013

import numpy as np
from mne import fiff
from sklearn.ensemble import RandomForestClassifier


filename = '/Users/sudregp/MEG_data/analysis/rest/good_PSDS.npz'
limits = [[1, 4], [4, 7], [8, 14], [14, 30], [30, 56], [64, 82], [82, 106], [124, 150]]

npzfile = np.load(filename)
psds = npzfile['psds']
adhd = npzfile['adhd']
freqs = npzfile['freqs']

ch_names = npzfile['info'][()]['ch_names']
picks = npzfile['picks'][()]
psd_channels = []
p = picks[::-1]
for i in p:
    psd_channels.append(ch_names.pop(i))
# now, select only the ones we want
look_for = ['M.F']
for sel in look_for:
    picks = fiff.pick_channels_regexp(psd_channels, sel)

band_psd = np.zeros([len(adhd), len(limits)])
for idx, bar in enumerate(limits):
    index = np.logical_and(freqs >= bar[0], freqs <= bar[1])
    band_psd[:, idx] = np.mean(np.mean(psds[:, :, index], axis=2), axis=1)

clf = RandomForestClassifier(n_estimators=10)
clf = clf.fit(band_psd, adhd)
clf.predict(band_psd)
