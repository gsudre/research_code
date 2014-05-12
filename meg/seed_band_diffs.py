''' Checks whether there is a group difference in the correlation map for a given seed '''

import mne
import numpy as np
from scipy import stats

seed = [10, -35, 2]
bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_pm2std.txt'
nvs_fname = '/Users/sudregp/data/meg/usable_nv_pm2std.txt'
adhds_fname = '/Users/sudregp/data/meg/usable_adhd_pm2std.txt'
persistent_fname = '/Users/sudregp/data/meg/persistent_pm2std.txt'
remitted_fname = '/Users/sudregp/data/meg/remitted_pm2std.txt'
sx_fname = '/Users/sudregp/data/meg/sx_counts.csv'
data_dir = '/Users/sudregp/data/meg/'
dir_out = '/Users/sudregp/data/results/meg/'

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

# find closest vertex to seed
if seed[0] < 0:
    hemis = 0  # LH
else:
    hemis = 1  # RH
coord = mne.vertex_to_mni(vertices=range(10242),hemis=hemis,subject='fsaverage')
dist = np.sqrt((coord[:,0] - seed[0])**2 + (coord[:,1] - seed[1])**2 + (coord[:,2] - seed[2])**2)
seed_vertex = np.argmin(dist)

# for each band, compute subject-based correlation map
for l_freq, h_freq in bands:
    nv_corrs = []
    adhd_corrs = []
    per_corrs = []
    rem_corrs = []
    print 'Band %d to %d Hz'%(l_freq, h_freq)
    cnt=0
    for s in subjs:
        print cnt+1, '/', len(subjs)
        fname = data_dir + 'morphed-lcmv-%dto%d-'%(l_freq,h_freq) + s
        stc = mne.read_source_estimate(fname)
        nverts = stc.data.shape[0]
        cor = []
        # this loop is faster than computing the entire mirror matrix
        for j in range(nverts):
            # need to scale up the values so they don't result in numerical error when computing correlation
            cor.append(stats.pearsonr(10**16*stc.data[seed_vertex,:], 10**16*stc.data[j,:])[0])
        if s in nvs:
            nv_corrs.append(cor)
        else:
            adhd_corrs.append(cor)
            if s in persistent:
                per_corrs.append(cor)
            else:
                rem_corrs.append(cor)
        cnt+=1

    # run statistical test for each vertex
    pvals = []
    pvals_nvVSper = []
    pvals_nvVSrem = []
    pvals_perVSrem = []
    for i in range(nverts):
        x = [p[i] for p in nv_corrs]
        y = [p[i] for p in adhd_corrs]
        pvals.append(stats.ttest_ind(x, y)[1])

        x = [p[i] for p in nv_corrs]
        y = [p[i] for p in per_corrs]
        pvals_nvVSper.append(stats.ttest_ind(x, y)[1])

        x = [p[i] for p in nv_corrs]
        y = [p[i] for p in rem_corrs]
        pvals_nvVSrem.append(stats.ttest_ind(x, y)[1])

        x = [p[i] for p in per_corrs]
        y = [p[i] for p in rem_corrs]
        pvals_perVSrem.append(stats.ttest_ind(x, y)[1])

    # save maps of pvalues
    res = mne.SourceEstimate(np.asarray([pvals]).T,[stc.lh_vertno,stc.rh_vertno],0,0,subject='fsaverage')
    res.save(dir_out + 'nvVSadhd-seed%d-%dto%d'%(seed_vertex,l_freq,h_freq))
    res = mne.SourceEstimate(np.asarray([pvals_nvVSper]).T,[stc.lh_vertno,stc.rh_vertno],0,0,subject='fsaverage')
    res.save(dir_out + 'nvVSper-seed%d-%dto%d'%(seed_vertex,l_freq,h_freq))
    res = mne.SourceEstimate(np.asarray([pvals_nvVSrem]).T,[stc.lh_vertno,stc.rh_vertno],0,0,subject='fsaverage')
    res.save(dir_out + 'nvVSrem-seed%d-%dto%d'%(seed_vertex,l_freq,h_freq))
    res = mne.SourceEstimate(np.asarray([pvals_perVSrem]).T,[stc.lh_vertno,stc.rh_vertno],0,0,subject='fsaverage')
    res.save(dir_out + 'perVSrem-seed%d-%dto%d'%(seed_vertex,l_freq,h_freq))



# res = env.load(ica_fname)
# time_pts = 241

# cnt = 0
# # split the subjects into their respective groups
# for s in subjs:
#     subj_power = np.mean(res['band_ICs'][:,:,cnt:cnt+time_pts], axis=2)
#     cnt += time_pts
    

# nbands = len(bands)
# nICs = 25 #nv_power[0].shape[1]
# # test each band / IC for group difference
# pvals = np.ones([nbands, nICs])
# pvals_nvVSper = np.ones([nbands, nICs])
# pvals_nvVSrem = np.ones([nbands, nICs])
# pvals_perVSrem = np.ones([nbands, nICs])
# for b in range(nbands):
#     for i in range(nICs):
#         x = [p[b, i] for p in nv_power]
#         y = [p[b, i] for p in adhd_power]
#         pvals[b, i] = stats.ttest_ind(x, y)[1]

#         x = [p[b, i] for p in nv_power]
#         y = [p[b, i] for p in per_power]
#         pvals_nvVSper[b, i] = stats.ttest_ind(x, y)[1]

#         x = [p[b, i] for p in nv_power]
#         y = [p[b, i] for p in rem_power]
#         pvals_nvVSrem[b, i] = stats.ttest_ind(x, y)[1]

#         x = [p[b, i] for p in per_power]
#         y = [p[b, i] for p in rem_power]
#         pvals_perVSrem[b, i] = stats.ttest_ind(x, y)[1]

# # here we assume that hi and inatt were constructed in the same order as adhd_power
# hi_pvals = np.ones([nbands, nICs])
# inatt_pvals = np.ones([nbands, nICs])
# for b in range(nbands):
#     for i in range(nICs):
#         y = [p[b, i] for p in adhd_power]
#         hi_pvals[b,i] = stats.pearsonr(y, hi)[1]
#         inatt_pvals[b,i] = stats.pearsonr(y, inatt)[1]
