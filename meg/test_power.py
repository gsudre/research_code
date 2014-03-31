import mne
import numpy as np
from scipy import stats


bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
nvs_fname = '/Users/sudregp/data/meg/usable_nv_pm2std.txt'
adhds_fname = '/Users/sudregp/data/meg/usable_adhd_pm2std.txt'
sx_fname = '/Users/sudregp/data/meg/sx_counts.csv'
data_dir = '/mnt/neuro/MEG_data/'
dir_out = '/users/sudregp/data/meg/'

nfid = open(nvs_fname, 'r')
afid = open(adhds_fname, 'r')
adhds = [line.rstrip() for line in afid]
nvs = [line.rstrip() for line in nfid]
subjs = [nvs] + [adhds]
sx = np.recfromcsv(sx_fname)
hi = [rec[2] for s in adhds for rec in sx if rec[0]==s]
inatt = [rec[1] for s in adhds for rec in sx if rec[0]==s]

# # running test for average over the whole brain
# ttest_sig = []
# hi_corr = []
# hi_corr_sig = []
# inatt_corr = []
# inatt_corr_sig = []
# for l_freq, h_freq in bands:
#     print 'Loading all subjects; band %d to %d Hz'%(l_freq, h_freq)
#     mean_power = []
#     for group in subjs:
#         group_power = []
#         for subj in group:
#             fname = dir_out + 'morphed-lcmv-%dto%d-'%(l_freq,h_freq) + subj
#             stc = mne.read_source_estimate(fname)
#             group_power.append(np.mean(stc.data))
#         mean_power.append(group_power)
#     pval = stats.ttest_ind(mean_power[0],mean_power[1])[1]
#     ttest_sig.append(pval)
#     r, p = stats.pearsonr(mean_power[1], hi)
#     hi_corr.append(r)
#     hi_corr_sig.append(p)
#     r, p = stats.pearsonr(mean_power[1], inatt)
#     inatt_corr.append(r)
#     inatt_corr_sig.append(p)

# running test for each individual vertex
ttest_sig = []
hi_corr = []
hi_corr_sig = []
inatt_corr = []
inatt_corr_sig = []
for l_freq, h_freq in bands:
    print 'Loading all subjects; band %d to %d Hz'%(l_freq, h_freq)
    mean_power = []
    for group in subjs:
        group_power = []
        for subj in group:
            fname = dir_out + 'morphed-lcmv-%dto%d-'%(l_freq,h_freq) + subj
            stc = mne.read_source_estimate(fname)
            group_power.append(np.mean(stc.data, axis=1))
        mean_power.append(np.array(group_power))
    nverts = mean_power[0].shape[1]
    ttest_sig.append(np.nan*np.ones([nverts,1]))
    hi_corr.append(np.nan*np.ones([nverts,1]))
    hi_corr_sig.append(np.nan*np.ones([nverts,1]))
    inatt_corr.append(np.nan*np.ones([nverts,1]))
    inatt_corr_sig.append(np.nan*np.ones([nverts,1]))
    for v in range(nverts):
        pval = stats.ttest_ind(mean_power[0][:,v],mean_power[1][:,v])[1]
        ttest_sig[-1][v] = pval
        r, p = stats.pearsonr(mean_power[1][:,v], hi)
        hi_corr[-1][v] = r
        hi_corr_sig[-1][v] = p
        r, p = stats.pearsonr(mean_power[1][:,v], inatt)
        inatt_corr[-1][v] = r
        inatt_corr_sig[-1][v] = p