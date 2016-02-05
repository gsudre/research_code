''' Generates correlations for a full matrix of all sources in fsaverage. Saves one matrix per subject/band so it's easy to access later. '''

import mne
import numpy as np

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
subjs_fname = '/Users/sudregp/data/meg/aligned_subjs.txt'
dir_out = '/mnt/neuro/MEG_data/correlations/'
data_dir = '/Users/sudregp/data/meg/'
nsources = 20484

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]

iu = np.triu_indices(nsources, k=1)
# for each band, compute subject-based correlation map
for l_freq, h_freq in bands:
    subj_corrs = []
    print 'Band %d to %d Hz'%(l_freq, h_freq)
    for cnt, s in enumerate(subjs):
        print cnt+1, '/', len(subjs), ':', s
        fname = data_dir + 'morphed-lcmv-%dto%d-'%(l_freq,h_freq) + s
        stc = mne.read_source_estimate(fname)
        corr = np.float16(np.corrcoef(stc.data))[iu]
        np.save(dir_out + 'all2allCorr-%dto%d-'%(l_freq,h_freq) + s, corr)
