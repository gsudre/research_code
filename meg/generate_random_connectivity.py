# Script to calculate connectivity in SAM time series per ROI
# by Gustavo Sudre, July 2014
import numpy as np
import mne
import os
import pylab as pl
import sys


subj = sys.argv[1]
home = os.path.expanduser('~')

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
method=['pli','imcoh','plv','wpli','pli2_unbiased','wpli2_debiased']
data_dir = home + '/data/meg/sam/'
nperms = 1000

# For each subject, we use the weight matrix to compute virtual electrodes
data = np.load(data_dir + subj + '_roi_data.npz')['data']
band_perms = []
for idx, band in enumerate(bands):
    perms=[]
    for k in range(nperms):
        rand_data = np.zeros_like(data[idx])
        for epoch in range(rand_data.shape[0]):
            for roi in range(rand_data.shape[1]):
                rand_data[epoch,roi,:] = pl.fftsurr(data[idx,epoch,roi,:])
        subj_conn = mne.connectivity.spectral_connectivity(rand_data, method=method, mode='multitaper', sfreq=300, fmin=band[0], fmax=band[1], faverage=True, n_jobs=1, mt_adaptive=False)[0]
        perms.append([np.nanmax(c) for c in subj_conn])
    band_perms.append(perms)
np.save(data_dir + '/perms/' + subj + '_roi_perm_connectivity', np.array(band_perms))
