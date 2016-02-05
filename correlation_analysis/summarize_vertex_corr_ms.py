# Summarizes the vertex-based subcortical correlation
import numpy as np
import os
import pylab as pl
import scipy
import mne


def r2z(r):
    return 0.5 * (np.log(1+r) - np.log(1-r))


def getZ(m1, m2):
    zbar1 = r2z(m1)
    zbar2 = r2z(m2)
    zs = (zbar1 - zbar2) / np.sqrt(1./(n1-3) + 1./(n2-3))
    pvals = scipy.stats.norm.sf(abs(zs))*2
    return zs, pvals


def showStats(zs, pvals):
    print 'Maximum Z:', np.nanmax(zs)
    print 'Good uncorrected pvals:', np.sum(pvals<thresh), '/', len(pvals)

    print 'Correcting with FDR:'
    clean_pvals = pvals[~np.isnan(pvals)]
    reject_fdr, adj_pvals = mne.stats.fdr_correction(clean_pvals, alpha=thresh, method='negcorr')
    print 'Good FDR pvals:', np.sum(adj_pvals<thresh), '/', len(adj_pvals)


# Note that vertices inside the same ROI will be highly correlated!
g1 = 'NV'
n1 = 64
g2 = 'persistent'
n2 = 32
fromR = ['thalamus']
toR = ['thalamus']
thresh = .05

print 'Loading data'
res1 = np.load('%s/data/results/structural/verts_MS_from%s_to%s_matchdiff_dsm5_2to1_%s.npz'%
                (os.path.expanduser('~'), fromR[0], '-'.join(toR), g1))
res2 = np.load('%s/data/results/structural/verts_MS_from%s_to%s_matchdiff_dsm5_2to1_%s.npz'%
                (os.path.expanduser('~'), fromR[0], '-'.join(toR), g2))

print 'Baseline'
zs, pvals = getZ(np.hstack([res1['ms'][0], res1['ms'][3]]), np.hstack([res2['ms'][0], res2['ms'][3]]))
showStats(zs,pvals)
print 'Last'
zs, pvals = getZ(np.hstack([res1['ms'][1], res1['ms'][4]]), np.hstack([res2['ms'][1], res2['ms'][4]]))
showStats(zs,pvals)
print 'Diff'
zs, pvals = getZ(np.hstack([res1['ms'][2], res1['ms'][5]]), np.hstack([res2['ms'][2], res2['ms'][5]]))
showStats(zs,pvals)
