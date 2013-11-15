# Summarizes the vertex-based subcortical correlation
import numpy as np
import os
import pylab as pl
import scipy
import mne


def r2z(r):
    return 0.5 * (np.log(1+r) - np.log(1-r))


# Note that vertices inside the same ROI will be highly correlated!
groups = ['NV', 'persistent']
method = 'delta'  # 'base','last','delta'
thresh = .05

print 'Loading data'
corrs = []
if method=='base':
    # take the Fisher r-to-z transform of all Rs
    print 'Calculating R to Z transformation'
    baseCor1 = r2z(res1['corrs'])
    baseCor2 = r2z(res2['corrs'])
    mat = (baseCor1 - baseCor2) / np.sqrt(1./(n1-3) + 1./(n2-3))
elif method=='last':
    print 'Calculating R to Z transformation'
    lastCor1 = r2z(res1['corrs'])
    lastCor2 = r2z(res2['corrs'])
    mat = (lastCor1 - lastCor2) / np.sqrt(1./(n1-3) + 1./(n2-3))
elif method=='delta':
    for g in groups:
        print g
        resb = np.load('%s/data/results/structural/verts_baseCorr_striatumRthamalusRmatchdiff_dsm5_2to1_%s.npz'% (os.path.expanduser('~'), g))
        resl = np.load('%s/data/results/structural/verts_lastCorr_striatumRthamalusRmatchdiff_dsm5_2to1_%s.npz'% (os.path.expanduser('~'), g))
        corrs.append(resl['corrs'] - resb['corrs'])
else:
    print('Error: did not recognize method.')

idx1 = np.array(range(6178))
idx2 = 6178 + np.array(range(3108))
data1 = [list(corrs[0][i, idx2]) for i in idx1]
data1 = [j for k in data1 for j in k]
data2 = [list(corrs[1][i, idx2]) for i in idx1]
data2 = [j for k in data2 for j in k]
theDiff = 1 - scipy.stats.spearmanr(data1, data2)[0]
