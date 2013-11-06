# Summarizes the vertex-based subcortical correlation
import numpy as np
import os
import pylab as pl
import scipy
import mne


def r2z(r):
    return 0.5 * (np.log(1+r) - np.log(1-r))


# Note that vertices inside the same ROI will be highly correlated!
g1 = 'NV'
n1 = 64
g2 = 'persistent'
n2 = 32
method = 'base'  # 'base','last','delta'
thresh = .05

print 'Loading data'
res1 = np.load('%s/data/results/structural/verts_%sCorr_matchdiff_dsm5_2to1_%s.npz'%
                (os.path.expanduser('~'), method, g1))
res2 = np.load('%s/data/results/structural/verts_%sCorr_matchdiff_dsm5_2to1_%s.npz'%
                (os.path.expanduser('~'), method, g2))
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
    print 'Calculating R to Z transformation'
    deltaCor1 = r2z(res1['corrs'])
    deltaCor2 = r2z(res2['corrs'])
    mat = (deltaCor1 - deltaCor2) / np.sqrt(1./(n1-3) + 1./(n2-3))
else:
    print('Error: do not recognize method.')


nverts = mat.shape[0]
# indexes of the triangular matrix (above the symetric diagonal)
print 'Getting upper indexes'
ui = np.triu_indices(nverts,k=1)
print 'Calculating p-values'
# 2-sided
zs = mat[ui[0],ui[1]]
pvals = scipy.stats.norm.sf(abs(zs))*2
print 'Maximum Z:', np.nanmax(zs)
print 'Good uncorrected pvals:', np.sum(pvals<thresh), '/', len(pvals)

print 'Correcting with FDR:'
clean_pvals = pvals[~np.isnan(pvals)]
reject_fdr, adj_pvals = mne.stats.fdr_correction(clean_pvals, alpha=thresh, method='negcorr')
print 'Good FDR pvals:', np.sum(adj_pvals<thresh), '/', len(adj_pvals)
