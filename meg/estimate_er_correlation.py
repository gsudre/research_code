# estimates the correlation among the data covariance matrices of different empty room recordings

import mne
import numpy as np
import pylab as pl

mats = []
er_fname = '/Users/sudregp/data/meg/empty_room_files.txt'
er_dir = '/Users/sudregp/data/meg_empty_room/'
fid = open(er_fname, 'r')
er_files = [line.rstrip() for line in fid]
noise_reg = .03

for er in er_files:
    er_raw = mne.fiff.Raw(er_dir + er, preload=True, compensation=3)
    picks = mne.fiff.pick_channels_regexp(er_raw.info['ch_names'], 'M..-*')
    # the later datasets are missing 2 channels, 'MLF25-1609', 'MLT31-1609', so we need to remove them if we want to do a correlation over time
    if len(picks)>271:
        picks = np.delete(picks, [32, 111])
    er_raw.filter(l_freq=1, h_freq=50, picks=picks)
    noise_cov = mne.compute_raw_data_covariance(er_raw, picks=picks)
    noise_cov = mne.cov.regularize(noise_cov, er_raw.info, mag=noise_reg)
    mats.append(noise_cov.data)

diags = [np.diag(m) for m in mats]
diags = np.array(diags)
corr = np.corrcoef(diags)
pl.imshow(corr)
pl.colorbar()