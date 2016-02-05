''' Makes a brain plot of seed correlations in a group '''

import mne
import numpy as np
from scipy.stats import t

seed_src = 4060
band = [8,13]
group = 'adhd'  # persistent, remission, adhd, nv
fdr = .05  # 0 for none

subjs_fname = '/Users/sudregp/data/meg/good_subjects.txt'
group_fname = '/Users/sudregp/data/meg/%s_subjs.txt'%group
data_dir = '/Users/sudregp/data/results/meg/'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
fid = open(group_fname, 'r')
this_group = [line.rstrip() for line in fid]
fid.close()

# load the pre-computed correlation data
fname = data_dir + 'corrs-seed%d-%dto%d-lh.stc'%(seed_src,band[0],band[1])
stc = mne.read_source_estimate(fname)

y = [s in this_group for s in subjs]
y = np.asarray(y).T
X = np.mean(stc.data[:,y], axis=1)

print 'Subjects in %s: %d'%(group,np.sum(y))
if fdr > 0:
    n = sum(y)
    # from http://www.danielsoper.com/statcalc3/calc.aspx?id=44
    tstat = X/np.sqrt((1-X**2)/(n-2))
    # t.sf gives the one tailed version
    pval = t.sf(tstat,n-1)*2
    reject_fdr, pval_fdr = mne.stats.fdr_correction(pval, alpha=fdr, method='indep')
    X[~reject_fdr] = 0

stc2 = mne.SourceEstimate(X[:,None], vertices=stc.vertno, tmin=0, tstep=0,subject='fsaverage')
brain = stc2.plot(hemi='both',fmin=min(X),fmid=(min(X)+(max(X)-min(X))/2),fmax=max(X))

