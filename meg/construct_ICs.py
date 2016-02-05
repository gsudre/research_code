import numpy as np
import mne
from scipy import stats
from sklearn.decomposition import FastICA


bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
g1_fname = '/Users/sudregp/data/meg/nv_subjs.txt'
g2_fname = '/Users/sudregp/data/meg/adhd_subjs.txt'
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_pm2std.txt'
data_dir = '/Users/sudregp/data/meg_diagNoise_noiseRegp03_dataRegp001/'

fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid = open(subjs_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
subjs = [line.rstrip() for line in fid]

# concatenate all subjects and apply ICA
band_ICs = []
for l_freq, h_freq in bands:
    print 'Concatenating sources in band %d to %d Hz'%(l_freq, h_freq)
    init_sources = 20500
    init_time = 38500
    # create huge array so we can add all the data and then resize it appropriately
    data = np.empty([init_sources, init_time])
    data[:] = np.nan
    cnt = 0
    subj_order = []
    for subj in subjs:
        if subj in g1+g2:
            fname = data_dir + 'morphed-lcmv-%dto%d-'%(l_freq,h_freq) + subj
            stc= mne.read_source_estimate(fname)
            # mean correcting and normalizing variance
            data[0:stc.data.shape[0], cnt:(cnt+stc.data.shape[1])] = \
                stats.mstats.zscore(stc.data, axis=1)
            cnt += stc.data.shape[1]
            subj_order.append(subj)
    data = data[:stc.data.shape[0], :cnt]

    # applying ICA and figuring out how each IC scores
    print 'Applying FastICA'
    ica = FastICA(n_components=30, random_state=0)
    ICs = ica.fit_transform(data.T).T

    band_ICs.append(ICs)
