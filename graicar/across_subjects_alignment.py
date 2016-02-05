
import os
home = os.path.expanduser('~')
import numpy as np
from scipy import stats
import itertools
import pylab as pl
import sys
from sklearn.metrics import normalized_mutual_info_score

if len(sys.argv) > 2:
    subj_file, freq_band = sys.argv[1:]
    res_dir = home + '/data/results/graicar/meg/'
elif len(sys.argv) > 1:
    subj_file = sys.argv[1]
    freq_band = None
    res_dir = home + '/data/results/graicar/fmri/'
else:
    # subj_file = home + '/tmp/good_nvs.txt'
    # freq_band = '8-13'
    # res_dir = home + '/data/results/graicar/meg/'
    subj_file = home + '/data/fmri/joel_nvs.txt'
    freq_band = None
    res_dir = home + '/data/results/graicar/fmri/demo/'
    subjs = ['subj1', 'subj2', 'subj3', 'subj4']


# top aligned ICs across subjects
ntop = 10
nperms = 1000
fid = open(subj_file, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
nsubj = len(subjs)


def calcNMI(xx, yy):
    nx = len(xx)
    ny = len(yy)
    n = min(nx, ny)
    nbin = np.ceil(n ** (float(1) / 3))

    [counts, xbins, ybins] = np.histogram2d(xx[:n], yy[:n], bins=nbin)
    h = counts / float(n)

    hy = np.sum(h, axis=0)
    hx = np.sum(h, axis=1)

    hx = -np.nansum(hx * np.log2(hx + np.spacing(1)))
    hy = -np.nansum(hy * np.log2(hy + np.spacing(1)))
    hxy = -np.nansum(h * np.log2(h + np.spacing(1)))

    return (hx + hy) / hxy - 1


def calcNMI2(xx, yy):
    nx = len(xx)
    ny = len(yy)
    n = min(nx, ny)
    nbin = np.ceil(n ** (float(1) / 3))
    rangex = (np.min(xx), np.max(xx))
    rangey = (np.min(yy), np.max(yy))

    xb = stats.binned_statistic(xx, xx, bins=nbin, range=rangex)[2]
    yb = stats.binned_statistic(yy, yy, bins=nbin, range=rangey)[2]

    return normalized_mutual_info_score(xb, yb)


# index to coordinate
def i2c(idx):
    s = 0
    while (idx - nics[s]) >= 0:
        idx -= nics[s]
        s += 1
    return s, idx


# coordinate (subject, ic) to index in matrix
def c2i(subj, ic):
    idx = np.sum(nics[:subj]) + ic
    return idx


all_ICs = []
nics = []
for s in subjs:
    print 'Loading subject %s' % s
    if freq_band is not None:
        fname = res_dir + '%s_%s_aligned.npz' % (s, freq_band)
    else:
        fname = res_dir + '%s_aligned.npz' % (s)
    all_ICs.append(np.load(fname)['average_ICs'])
    nics.append(all_ICs[-1].shape[0])
nics = np.array(nics)

# we need to be careful because, when in time, not all subjects might have the same number of time points. So, we need to construct the full similarity matrix slowly. We use the maximum amount of time points we can between subjects
print 'Constructing Full Similarity Matrix'
fsm = np.zeros([np.sum(nics), np.sum(nics)])
fsm[:] = np.nan
# the matrix is symmetric for now, but won't be in the future, so calculate both triu and tril
# we structure fsm as all comps for subj 1, then all comps for subj 2, and etc
for i in range(nsubj):
    ptr1 = c2i(i, 0)
    for j in range(nsubj):
        ptr2 = c2i(j, 0)
        print 'Subjects %d <-> %d' % (i + 1, j + 1)
        tlim = min(all_ICs[i].shape[1], all_ICs[j].shape[1])
        for ic1 in range(nics[i]):
            for ic2 in range(nics[j]):
                if i == j and ic1 == ic2:
                    res = 1
                else:
                    # # NMI
                    # res = calcNMI(all_ICs[i][ic1, :], all_ICs[j][ic2, :])

                    # correlation
                    res = np.corrcoef(all_ICs[i][ic1, :tlim],
                                      all_ICs[j][ic2, :tlim])
                    res = np.abs(res[0, 1])

                    # # different way to compute NMI
                    # res = calcNMI2(all_ICs[i][ic1, :], all_ICs[j][ic2, :])
                fsm[c2i(i, ic1), c2i(j, ic2)] = res

# standardize to Z-score within each row in each block
print 'Standardizing within blocks'
zrow = fsm.copy()
for row in range(zrow.shape[0]):
    for s in range(nsubj):
        # within subject blocks become all zeros
        row_subj = i2c(row)[0]
        ptr = c2i(s, 0)
        if row_subj == s:
            zrow[row, ptr:(ptr + nics[s])] = 0
        else:
            zrow[row, ptr:(ptr + nics[s])] = stats.mstats.zscore(zrow[row, ptr:(ptr + nics[s])])

# This is not explicit in the paper, but if we're going to be looking at maximum contributions, we need to use the absolute of the z-score from here on. We can look at the sign again later, when averaging the components
zrow = np.abs(zrow)

# identify local maximum within each row in each block
print 'Finding local maximum'
zmax = zrow.copy()
for row in range(zrow.shape[0]):
    for s in range(nsubj):
        ptr = c2i(s, 0)
        mymax = np.max(zrow[row, ptr:(ptr + nics[s])])
        imax = np.argmax(zrow[row, ptr:(ptr + nics[s])])
        zmax[row, ptr:(ptr + nics[s])] = 0
        zmax[row, ptr + imax] = mymax

# Calculate weight matrix and popularity rank
print 'Computing popularity rank'
W = np.multiply(zmax, zmax.T)
popularity = np.sum(W, axis=0)
p_rank = np.argsort(popularity)[::-1]
szrow = zrow + zrow.T

# Generating null distribution of subject contributions
print 'Generating null distribution'
perms = np.zeros([nperms, nsubj])
perms[:] = np.nan
for p in range(nperms):
    rand_rmat = np.zeros([nsubj, nsubj])
    rand_rmat[:] = np.nan
    rand_ics = [np.random.randint(nics[s]) for s in range(nsubj)]
    for s1, s2 in itertools.combinations(range(nsubj), 2):
        ptr1 = c2i(s1, rand_ics[s1])
        ptr2 = c2i(s2, rand_ics[s2])
        rand_rmat[s1, s2] = szrow[ptr1, ptr2]
        rand_rmat[s2, s1] = szrow[ptr2, ptr1]
    perms[p, :] = np.nanmax(rand_rmat, axis=1)

# Align ICs based on rank amd maximum similarity
print 'Aligning components'
# list of [subj, ic] pairs
aligned_ICs = []
# list of arrays of nsubj x nsubj shape
rep_mats = []
loadings = []
confidence = []
for row in p_rank:
    # check that this row hasn't been removed yet
    if np.sum(szrow[row, :] == -np.inf) < szrow.shape[1]:
        init_subj, init_ic = i2c(row)
        align = [[init_subj, init_ic]]
        used_idx = [row]
        for s in range(nsubj):
            # don't include the subject with the initial IC
            if s != init_subj:
                ptr = c2i(s, 0)
                imax = np.argmax(szrow[row, ptr:(ptr + nics[s])])
                align.append([s, imax])
                used_idx.append(imax + ptr)
        # constructing reproducibility matrix
        rmat = np.zeros([nsubj, nsubj])
        rmat[:] = np.nan
        for i, j in itertools.combinations(used_idx, 2):
            s1, c1 = i2c(i)
            s2, c2 = i2c(j)
            rmat[s1, s2] = szrow[i, j]
            rmat[s2, s1] = szrow[j, i]
        # removing the chosen ICs from further consideration
        for i in used_idx:
            szrow[i, :] = -np.inf
            szrow[:, i] = -np.inf
        aligned_ICs.append(align)
        rep_mats.append(rmat)
        mult = np.nanmean(rmat, axis=0)
        loadings.append(mult)
        ci = [stats.percentileofscore(perms[:, s], mult[s]) for s in range(nsubj)]
        confidence.append(ci)

# Save results because re-construction depends on time or spatial ICA
if freq_band is not None:
    fname = res_dir + 'group_' + freq_band + '_aligned'
else:
    fname = res_dir + 'group_aligned'
np.savez(fname, subjs=subjs, aligned_ICs=aligned_ICs, rep_mats=rep_mats,
         loadings=loadings, confidence=confidence)

# make one plot per aligned IC
print 'Making figures'
for i in range(np.min(nics)):
    pl.figure(figsize=(15, 4))
    pl.subplot(1, 3, 1)
    pl.imshow(rep_mats[i], interpolation='none')
    pl.xticks(range(nsubj))
    pl.yticks(range(nsubj))
    pl.xlabel('Subjects')
    pl.ylabel('Contribution')
    pl.colorbar()
    pl.subplot(1, 3, 2)
    pl.bar(range(nsubj), loadings[i], color='k')
    pl.xlabel('Subjects')
    pl.ylabel('Contribution')
    pl.xticks(range(nsubj))
    pl.subplot(1, 3, 3)
    pl.bar(range(nsubj), confidence[i], color='k')
    pl.xlabel('Subjects')
    pl.ylabel('Confidence of contribution')
    pl.xticks(range(nsubj))
    pl.ylim([0, 100])
    pl.savefig(fname + 'IC%02d.png' % i)
    pl.close()
