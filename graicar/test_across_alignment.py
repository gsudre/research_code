
import os
home = os.path.expanduser('~')
import numpy as np
from scipy import stats, io
import itertools
import pylab as pl
import sys

if len(sys.argv) > 2:
    subj_file, freq_band = sys.argv[1:]
    res_dir = home + '/data/results/graicar/meg/'
elif len(sys.argv) > 1:
    subj_file = sys.argv[1]
    freq_band = None
    res_dir = home + '/data/results/graicar/fmri/'
else:
    subj_file = home + '/tmp/good_nvs.txt'
    freq_band = '8-13'
    res_dir = home + '/data/results/graicar/fmri/demo/'
    # subj_file = 'subj1'
    # freq_band = None
    # es_dir = home + '/data/results/graicar/fmri/'


# top aligned ICs across subjects
nperms = 1000
fid = open(subj_file, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
subjs = ['subj1', 'subj2', 'subj3', 'subj4']
nsubj = len(subjs)


def calcNMI(xx, yy):
    ncell = max(np.max(xx), np.max(yy))
    nx = len(xx)
    ny = len(yy)
    total = min(nx, ny)

    # nbin = np.ceil(n ** (float(1) / 3))
    counts = np.zeros([ncell, ncell])
    for n in range(total):
        indexx = xx[n] - 1
        indexy = yy[n] - 1
        counts[indexx, indexy] = counts[indexx, indexy] + 1

    # [counts, xbins, ybins] = np.histogram2d(xx[:n], yy[:n], bins=nbin)
    h = counts / float(total)

    hy = np.sum(h, axis=0)
    hx = np.sum(h, axis=1)

    hx = -np.nansum(hx * np.log2(hx))
    hy = -np.nansum(hy * np.log2(hy))
    hxy = -np.nansum(h * np.log2(h))

    return (hx + hy) / hxy


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
    fname = home + '/Downloads/demo/%s/rest/ICA/RAICAR/bin_RAICAR_ICA_aveMap.nii.gz1.mat' % s
    all_ICs.append(io.loadmat(fname)['comp'])
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
                # res = np.corrcoef(all_ICs[i][ic1, :tlim],
                #                   all_ICs[j][ic2, :tlim])
                # fsm[ptr1 + ic1, ptr2 + ic2] = np.abs(res[0, 1])
                res = calcNMI(all_ICs[i][ic1, :], all_ICs[j][ic2, :])
                fsm[c2i(i, ic1), c2i(j, ic2)] = res

# standardize to Z-score within each row in each block
print 'Standardizing within blocks'
zrow = fsm.copy()
for row in range(zrow.shape[0]):
    for s in range(nsubj):
        ptr = c2i(i, 0)
        zrow[row, ptr:(ptr + nics[s])] = stats.mstats.zscore(zrow[row, ptr:(ptr + nics[s])])

# identify local maximum within each row in each block
print 'Finding local maximum'
zmax = zrow.copy()
for row in range(zrow.shape[0]):
    for s in range(nsubj):
        ptr = c2i(i, 0)
        mymax = max(zrow[row, ptr:(ptr + nics[s])])
        imax = np.argmax(zrow[row, ptr:(ptr + nics[s])])
        zmax[row, ptr:(ptr + nics[s])] = 0
        zmax[row, imax] = mymax

# Calculate weight matrix and popularity rank
print 'Computing popularity rank'
W = np.dot(zmax, zmax.T)
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
        ptr1 = c2i(s1, 0)
        ptr2 = c2i(s2, 0)
        rand_rmat[s1, s2] = szrow[ptr1 + rand_ics[s1],
                                  ptr2 + rand_ics[s2]]
        rand_rmat[s2, s1] = szrow[ptr2 + rand_ics[s2],
                                  ptr1 + rand_ics[s1]]
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
    if np.sum(szrow[row, :] == -1) < szrow.shape[1]:
        init_subj, init_ic = i2c(row)
        align = [[init_subj, init_ic]]
        used_idx = [row]
        for s in range(nsubj):
            # don't include the subject with the initial IC
            if s != init_subj:
                ptr = c2i(s, 0)
                imax = np.argmax(szrow[row, ptr:(ptr + nics[s])])
                subj, ic = i2c(imax + ptr)
                align.append([subj, ic])
                used_idx.append(imax + ptr)
        # constructing reproducibility matrix
        rmat = np.zeros([nsubj, nsubj])
        rmat[:] = np.nan
        for i, j in itertools.combinations(used_idx, 2):
            s1, c1 = i2c(i)
            s2, c2 = i2c(j)
            rmat[s1, s2] = np.abs(szrow[i, j])
            rmat[s2, s1] = np.abs(szrow[j, i])
        # removing the chosen ICs from further consideration
        for i in used_idx:
            szrow[i, :] = -1
            szrow[:, i] = -1
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
