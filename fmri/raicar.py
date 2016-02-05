
import os
home = os.path.expanduser('~')
import numpy as np
import itertools
import pylab as pl
from scipy import stats
import glob


res_dir = home + '/data/fmri_example11_all/ica/'

nbins = 10  # to determine correlation cutoff

fname = res_dir + 'catFamAndSibsElbowZeroFilled'
files = glob.glob(fname + '_R??.npz')
nreals = len(files)
all_ICs = []
for fidx, f in enumerate(files):
    print 'Loading realization %d of %d' % (fidx+1, nreals)
    all_ICs.append(np.load(f)['ICs'])
# just so we can carry it forward later
res = np.load(f)
if 'subjs' in res.keys():
    subjs = np.load(f)['subjs']
    delme = np.load(f)['delme']
else:
    subjs, delme = None, None

ncomps = all_ICs[-1].shape[0]
# this makes all_ICs 2D, with all ncomps for nrep=1, then all ncomps for nrep=2, and etc
all_ICs = np.array(all_ICs).reshape(nreals * ncomps, -1)

# the cross-realization correlation matrix is nreals*ncomps by nreals*ncomps
print 'Computing correlations across all components'
crcm = np.corrcoef(all_ICs)
crcm_abs = np.abs(np.triu(crcm, k=1))

# determine threshold based on valley of CRCM histogram
u_idx = np.triu_indices(crcm.shape[0], k=1)
[bins, centers, patches] = pl.hist(np.abs(crcm)[u_idx], bins=nbins)
cc_threshold = .8  # centers[np.argmin(bins)]
print 'Correlation threshold: %.2f' % cc_threshold

# because we only pay attention at the magnitude of the connections, when we remove a given cell from consideration we mark it as -1. The lower part of the matrix has 0s, and it also has meaning behind it (low connection)
print 'Aligning components'
aligned_ics = []  # list of lists
for ic in range(ncomps):
    max_corr_idx = np.argmax(crcm_abs)
    idx = np.unravel_index(max_corr_idx, crcm_abs.shape)
    # like in the original RAICAR paper, we discover the realization and ICs
    re = [d / ncomps for d in idx]
    ics = [d % ncomps for d in idx]
    # list of (realization, IC) pairs
    this_aligned = [[r, i] for r, i in zip(re, ics)]
    # mark the correlation and realizations as used
    crcm_abs[idx] = -1
    used_idx = [r*ncomps + i for r in re for i in range(ncomps)]
    avail_re = np.array([True] * nreals * ncomps, dtype=bool)
    avail_re[used_idx] = False
    # each aligned component has nreals IC realizations
    while len(this_aligned) < nreals:
        # trying to find which IC best matches m and n in each realization, other than the initial 2 we identified
        best_m = np.argmax(crcm_abs[idx[0], avail_re])
        best_n = np.argmax(crcm_abs[avail_re, idx[1]])
        if crcm_abs[idx[0], avail_re][best_m] > crcm_abs[avail_re, idx[1]][best_n]:
            j = np.nonzero(avail_re)[0][best_m]
        else:
            j = np.nonzero(avail_re)[0][best_n]
        # make that particular IC-Iter as used
        crcm_abs[:, j] = -1
        crcm_abs[j, :] = -1
        re = j / ncomps
        ic = j % ncomps
        # update order list and available realization table
        this_aligned.append([re, ic])
        # mark the correlation and realization as used
        used_idx = [re*ncomps + i for i in range(ncomps)]
        avail_re[used_idx] = False
    # make sure the two initial components are not used again
    crcm_abs[:, idx[1]] = -1
    crcm_abs[idx[0], :] = -1
    aligned_ics.append(this_aligned)

# compute cross-correlations between aligned ICs, and the reproducibility index for all components
print 'Computing cross-correlation among aligned components'
all_ccs = []
rep_index = []
for ac in aligned_ics:
    ccs = []
    for ic1, ic2 in itertools.combinations(ac, 2):
        idx1 = ic1[0] * ncomps + ic1[1]
        idx2 = ic2[0] * ncomps + ic2[1]
        ccs.append(np.abs(np.corrcoef(all_ICs[idx1, :], all_ICs[idx2, :])[0, 1]))
    rep_index.append(np.sum(np.array(ccs) > cc_threshold))
    all_ccs.append(ccs)

# let's average the ICs after alignment. We also compute the normalized reproducibility score, based on how many points it can actually add up
mymax = float(nreals*(nreals-1)/2)
# remove ICs that have lower than 50% of the max reproducibility index
rep_index = np.array(rep_index) / mymax
average_scores = rep_index[rep_index > .5]
aligned_order = np.argsort(average_scores)[::-1]
average_ICs = np.zeros([len(aligned_order), all_ICs.shape[1]])
average_scores = average_scores[aligned_order]
# only include in the average the ICs that have at least one cc higher than threshold
cnt = 0
for i in aligned_order:
    comb_order = list(itertools.combinations(aligned_ics[i], 2))
    avg_idx = []
    for ic in aligned_ics[i]:
        my_ccs = np.array([pos for pos, comb in enumerate(comb_order) if ic in comb])
        if np.sum(np.array(all_ccs[i])[my_ccs] > cc_threshold) > 0:
            avg_idx.append(ic[0] * ncomps + ic[1])
    # in the MATLAB RAICAR code, he takes the z-score first, then add or subtract the IC based on the sign of the correlation
    ics = all_ICs[avg_idx, :]
    ics = stats.zscore(ics, axis=1)
    signs = np.sign(np.corrcoef(ics))
    avg_order = list(itertools.combinations(range(len(avg_idx)), 2))
    for j, k in avg_order:
        average_ICs[cnt, :] += (ics[j, :] + signs[j, k] * ics[k, :])
    average_ICs[cnt, :] /= len(avg_order)
    cnt += 1

fname = fname + '_aligned_corr%.2f' % (cc_threshold)
np.savez(fname, average_ICs=average_ICs, average_scores=average_scores,
         cc_threshold=cc_threshold, subjs=subjs, delme=delme)

print 'Found %d components.' % len(average_scores)

# make plot for average scores and average correlation with SD
all_order = np.argsort(rep_index)[::-1]
pl.figure(figsize=(15, 5))
pl.subplot(1, 3, 1)
pl.bar(range(ncomps), rep_index[all_order], color='k')
pl.xlabel('Components')
pl.ylabel('Normalized reproducibility')
pl.subplot(1, 3, 2)
mean_ccs = [np.nanmean(all_ccs[i]) for i in all_order]
sd_ccs = [np.nanstd(all_ccs[i]) for i in all_order]
pl.bar(range(ncomps), mean_ccs, color='k', yerr=sd_ccs, ecolor='r')
pl.xlabel('Components')
pl.ylabel('Mean similarity')
pl.subplot(1, 3, 3)
pl.hist(np.abs(crcm)[u_idx], bins=nbins)
pl.title('corr_thresh = %.2f' % cc_threshold)
pl.savefig(fname + '.png')
