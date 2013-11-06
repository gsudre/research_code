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
        resb = np.load('%s/data/results/structural/verts_baseCorr_matchdiff_dsm5_2to1_%s.npz'% (os.path.expanduser('~'), g))
        resl = np.load('%s/data/results/structural/verts_lastCorr_matchdiff_dsm5_2to1_%s.npz'% (os.path.expanduser('~'), g))
        corrs.append(resl['corrs'] - resb['corrs'])
else:
    print('Error: did not recognize method.')


nverts = corrs[0].shape[0]
# indexes of the triangular matrix (above the symetric diagonal)
print 'Getting upper indexes'
ui = np.triu_indices(nverts,k=1)
print 'Calculating distance between groups'
theDist = 1 - scipy.stats.spearmanr(corrs[0][ui], corrs[1][ui])[0]
