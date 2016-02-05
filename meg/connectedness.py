''' Simulates Steve's connectedness analysis, but in MEG '''

import mne
import numpy as np

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
# bands = [[13, 30], [30, 50]]
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_pm2std.txt'
dir_out = '/Users/sudregp/data/meg_diagNoise_noiseRegp03_dataRegp001/'
data_dir = '/Users/sudregp/data/meg_diagNoise_noiseRegp03_dataRegp001/'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]

# for each band, compute subject-based correlation map
for l_freq, h_freq in bands:
    print 'Band %d to %d Hz'%(l_freq, h_freq)
    for cnt, s in enumerate(subjs):
        print cnt+1, '/', len(subjs), ':', s
        fname = data_dir + 'morphed-lcmv-%dto%d-'%(l_freq,h_freq) + s
        stc = mne.read_source_estimate(fname)
        conn = np.mean(np.corrcoef(stc.data), axis=0)
        res = mne.SourceEstimate(conn[:,None],[stc.lh_vertno,stc.rh_vertno],0,1)
        res.save(dir_out + 'connectedness-%dto%d-%s'%(l_freq,h_freq,s))