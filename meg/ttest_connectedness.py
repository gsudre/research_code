import mne
import numpy as np
from scipy import stats


bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
g1_fname = '/Users/sudregp/data/meg/nv_subjs.txt'
g2_fname = '/Users/sudregp/data/meg/persistent_subjs.txt'
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_pm2std.txt'
# subjs_fname = '/Users/sudregp/data/meg/clean_subjs122.txt'
data_dir = '/Users/sudregp/data/meg_diagNoise_noiseRegp03_dataRegp001/'

fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid = open(subjs_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
subjs = [line.rstrip() for line in fid]

all_stats = []
for l_freq, h_freq in bands:
    print 'Band %d to %d Hz'%(l_freq, h_freq)
    corrs1 = []
    corrs2 = []
    for s in subjs:
        fname = data_dir + 'connectedness-%dto%d-%s-lh.stc'%(l_freq,h_freq,s)
        stc = mne.read_source_estimate(fname)
        if s in g1:
            corrs1.append(np.arctanh(stc.data))
        elif s in g2:
            corrs2.append(np.arctanh(stc.data))
    nverts = corrs1[0].shape[0]
    corrs1 = np.array(corrs1).squeeze()
    corrs2 = np.array(corrs2).squeeze()
    val = [stats.ttest_ind(corrs1[:,i],corrs2[:,i]) for i in range(nverts)]
    pvals = [i[1] for i in val]
    tstats = [i[0] for i in val]
    all_stats.append([tstats, pvals, [np.mean(corrs1,axis=0), np.mean(corrs2,axis=0)]])
    print 'Sources < .05 uncorrected:', sum(np.array(pvals)<.05)

# X = 1-np.array(all_stats[4][1])[:,None]
# stc2 = mne.SourceEstimate(X, vertices=stc.vertno, tmin=0, tstep=0,subject='fsaverage')
# brain = stc2.plot(hemi='both',fmin=.95,fmid=.975,fmax=1)
