import mne
import numpy as np
from scipy import stats


bands = [[1, 4]]#, [4, 8], [8, 13], [13, 30], [30, 50]]
nvs_fname = '/Users/sudregp/data/meg/nv_subjs.txt'
adhds_fname = '/Users/sudregp/data/meg/adhd_subjs.txt'
subjs_fname = '/Users/sudregp/data/meg/good_subjects.txt'
data_dir = '/mnt/neuro/MEG_data/correlations/'
dir_out = '/users/sudregp/data/meg/'

nfid = open(nvs_fname, 'r')
afid = open(adhds_fname, 'r')
fid = open(subjs_fname, 'r')
adhds = [line.rstrip() for line in afid]
nvs = [line.rstrip() for line in nfid]
subjs = [line.rstrip() for line in fid]

for l_freq, h_freq in bands:
    corrs1 = []
    corrs2 = []
    for sidx, subj in enumerate(subjs):
        print 'Loading subject %d/%d'%(sidx+1,len(subjs))
        res = np.load(data_dir + 'all2allCorr-%dto%d-%s.npy'%(l_freq,h_freq,subj))
        if subj in nvs:
            corrs1.append(res)
        else:
            corrs2.append(res)
    nverts = corrs1[0].shape[0]
    print 'Converting lists to arrays'
    corrs1 = np.array(corrs1,dtype=float16)
    corrs2 = np.array(corrs2,dtype=float16)
    print 'Pre-allocating result arrays'
    pvals = np.empty([nverts, nverts],dtype=np.float16)
    pvals[:] = np.nan
    tstats = pvals.copy()
    print 'Computing statistics'
    for i in range(nverts):
        for j in range(i+1, nverts):
            tstats[i,j],pvals[i,j] = stats.ttest_ind(corrs1[:,i,j],corrs2[:,i,j])

# # running test for average over the whole brain
# ttest_sig = []
# hi_corr = []
# hi_corr_sig = []
# inatt_corr = []
# inatt_corr_sig = []
# for l_freq, h_freq in bands:
#     print 'Loading all subjects; band %d to %d Hz'%(l_freq, h_freq)
#     mean_power = []
#     for group in [adhds, nvs]:
#         group_power = []
#         for subj in subjs:
#             if subj in group:
#                 fname = dir_out + 'morphed-lcmv-%dto%d-'%(l_freq,h_freq) + subj
#                 stc = mne.read_source_estimate(fname)
#                 group_power.append(np.mean(stc.data))
#         mean_power.append(group_power)
#     pval = stats.ttest_ind(mean_power[0],mean_power[1])[1]
#     ttest_sig.append(pval)

#     # r, p = stats.pearsonr(mean_power[1], hi)
#     # hi_corr.append(r)
#     # hi_corr_sig.append(p)
#     # r, p = stats.pearsonr(mean_power[1], inatt)
#     # inatt_corr.append(r)
#     # inatt_corr_sig.append(p)

# # running test for each individual vertex
# ttest_sig = []
# hi_corr = []
# hi_corr_sig = []
# inatt_corr = []
# inatt_corr_sig = []
# for l_freq, h_freq in bands:
#     print 'Loading all subjects; band %d to %d Hz'%(l_freq, h_freq)
#     mean_power = []
#     for group in [adhds, nvs]:
#         group_power = []
#         for subj in subjs:
#             if subj in group:
#                 fname = dir_out + 'morphed-lcmv-%dto%d-'%(l_freq,h_freq) + subj
#                 stc = mne.read_source_estimate(fname)
#                 group_power.append(np.mean(stc.data, axis=1))
#         mean_power.append(np.array(group_power))
#     nverts = mean_power[0].shape[1]
#     ttest_sig.append(np.nan*np.ones([nverts,1]))
    # hi_corr.append(np.nan*np.ones([nverts,1]))
    # hi_corr_sig.append(np.nan*np.ones([nverts,1]))
    # inatt_corr.append(np.nan*np.ones([nverts,1]))
    # inatt_corr_sig.append(np.nan*np.ones([nverts,1]))
    # for v in range(nverts):
    #     pval = stats.ttest_ind(mean_power[0][:,v],mean_power[1][:,v])[1]
    #     ttest_sig[-1][v] = pval
    #     r, p = stats.pearsonr(mean_power[1][:,v], hi)
    #     hi_corr[-1][v] = r
    #     hi_corr_sig[-1][v] = p
    #     r, p = stats.pearsonr(mean_power[1][:,v], inatt)
    #     inatt_corr[-1][v] = r
    #     inatt_corr_sig[-1][v] = p