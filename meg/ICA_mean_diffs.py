''' Checks whether there is a group difference in the mean power of each ICs '''

import mne
import numpy as np
from scipy import stats
import env


bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_pm2std.txt'
ica_fname = '/Users/sudregp/data/meg/ICA.npz'
nvs_fname = '/Users/sudregp/data/meg/usable_nv_pm2std.txt'
adhds_fname = '/Users/sudregp/data/meg/usable_adhd_pm2std.txt'
persistent_fname = '/Users/sudregp/data/meg/persistent_pm2std.txt'
remitted_fname = '/Users/sudregp/data/meg/remitted_pm2std.txt'
sx_fname = '/Users/sudregp/data/meg/sx_counts.csv'
data_dir = '/mnt/neuro/MEG_data/'
dir_out = '/users/sudregp/data/meg/'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
nfid = open(nvs_fname, 'r')
afid = open(adhds_fname, 'r')
pfid = open(persistent_fname, 'r')
rfid = open(remitted_fname, 'r')
adhds = [line.rstrip() for line in afid]
nvs = [line.rstrip() for line in nfid]
persistent = [line.rstrip() for line in pfid]
remitted = [line.rstrip() for line in rfid]
sx = np.recfromcsv(sx_fname)
hi = [rec[2] for s in subjs for rec in sx if rec[0]==s]
inatt = [rec[1] for s in subjs for rec in sx if rec[0]==s]

res = env.load(ica_fname)
time_pts = 241
nv_power = []
adhd_power = []
per_power = []
rem_power = []
cnt = 0
# split the subjects into their respective groups
for s in subjs:
    subj_power = np.mean(res['band_ICs'][:,:,cnt:cnt+time_pts], axis=2)
    cnt += time_pts
    if s in nvs:
        nv_power.append(subj_power)
    else:
        adhd_power.append(subj_power)
        if s in persistent:
            per_power.append(subj_power)
        else:
            rem_power.append(subj_power)

nbands = len(bands)
nICs = 25 #nv_power[0].shape[1]
# test each band / IC for group difference
pvals = np.ones([nbands, nICs])
pvals_nvVSper = np.ones([nbands, nICs])
pvals_nvVSrem = np.ones([nbands, nICs])
pvals_perVSrem = np.ones([nbands, nICs])
for b in range(nbands):
    for i in range(nICs):
        x = [p[b, i] for p in nv_power]
        y = [p[b, i] for p in adhd_power]
        pvals[b, i] = stats.ttest_ind(x, y)[1]

        x = [p[b, i] for p in nv_power]
        y = [p[b, i] for p in per_power]
        pvals_nvVSper[b, i] = stats.ttest_ind(x, y)[1]

        x = [p[b, i] for p in nv_power]
        y = [p[b, i] for p in rem_power]
        pvals_nvVSrem[b, i] = stats.ttest_ind(x, y)[1]

        x = [p[b, i] for p in per_power]
        y = [p[b, i] for p in rem_power]
        pvals_perVSrem[b, i] = stats.ttest_ind(x, y)[1]

# here we assume that hi and inatt were constructed in the same order as adhd_power
hi_pvals = np.ones([nbands, nICs])
inatt_pvals = np.ones([nbands, nICs])
for b in range(nbands):
    for i in range(nICs):
        y = [p[b, i] for p in adhd_power]
        hi_pvals[b,i] = stats.pearsonr(y, hi)[1]
        inatt_pvals[b,i] = stats.pearsonr(y, inatt)[1]
