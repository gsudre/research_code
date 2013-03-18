import numpy as np
from scipy import stats
import env
import mne

pcc = [50, 46]
par = [14, 62]
mpfc = [28, 52]

pcc = [51, 47]
par = [15, 63]
mpfc = [29, 53]

res = np.load(env.results + 'plis_good_subjects.npz')
plis = res['plis'][()]


def summarize_data(plis, fname):

    fid = open(fname, 'r')

    # counting how many subjects we have
    subjs = fid.readlines()
    num_subj = 0
    for subj in subjs:
        if subj.rstrip() > 0:
            num_subj += 1

    num_bands = len(plis[plis.keys()[0]])
    num_labels = plis[plis.keys()[0]][0].shape[0]

    # construct the arrays that we'll average over. They need to be subj x band x labels x labels
    all_plis = np.zeros([num_subj, num_bands, num_labels, num_labels])

    for ids, subj in enumerate(subjs):
        if subj.rstrip() > 0:
            for band in range(num_bands):
                all_plis[ids, band, :, :] = plis[subj.rstrip()][band]

    mean_pli = np.mean(all_plis, axis=0)
    std_pli = np.std(all_plis, axis=0)

    return mean_pli, std_pli, all_plis

meanNV, stdNV, NV = summarize_data(plis, env.maps + 'MEG_adults_good_NVs.txt')
meanADHD, stdADHD, ADHD = summarize_data(plis, env.maps + 'MEG_adults_good_ADHDs.txt')

# now we run a t-test for each label combination we want, in all bands

all_ps = []
for b in range(NV.shape[1]):
    for l1 in pcc:
        for l2 in par:
            if l2 > l1:
                A = NV[:, b, l2, l1]
                B = ADHD[:, b, l2, l1]
            else:
                A = NV[:, b, l1, l2]
                B = ADHD[:, b, l1, l2]

            t, p = stats.ttest_ind(A, B, axis=0, equal_var=True)
            all_ps.append(p)

    for l1 in pcc:
        for l2 in mpfc:
            if l2 > l1:
                A = NV[:, b, l2, l1]
                B = ADHD[:, b, l2, l1]
            else:
                A = NV[:, b, l1, l2]
                B = ADHD[:, b, l1, l2]

            t, p = stats.ttest_ind(A, B, axis=0, equal_var=True)
            all_ps.append(p)

    for l1 in mpfc:
        for l2 in par:
            if l2 > l1:
                A = NV[:, b, l2, l1]
                B = ADHD[:, b, l2, l1]
            else:
                A = NV[:, b, l1, l2]
                B = ADHD[:, b, l1, l2]

            t, p = stats.ttest_ind(A, B, axis=0, equal_var=True)
            all_ps.append(p)

reject_fdr, pval_fdr = mne.stats.fdr_correction(all_ps)


def mirror(A):
    # makes A a mirror matrix (mirrowing the lower triangle)
    n = A.shape[0]
    A[np.triu_indices(n)] = A.T[np.triu_indices(n)]
    return A


#################

# since the above didn't yield anything, let's try to do the analysis in the paper and see how many ROIs have a significant connection profile
res = np.load('/Users/sudregp/results/compiled_rand.npz')
rand_adhd = np.mean(res['rand_ADHD'][()], axis=1)
rand_nv = np.mean(res['rand_NV'][()], axis=1)
nv_mean_rand_pli = np.zeros([100, 5, 68])
adhd_mean_rand_pli = np.zeros([100, 5, 68])
for r in range(100):
    for b in range(5):
        m = mirror(rand_nv[r, b, :, :])
        # m = np.ma.masked_equal(rand_nv[r, b, :, :], 0)
        nv_mean_rand_pli[r, b, :] = np.mean(m, axis=0)
        m = mirror(rand_adhd[r, b, :, :])
        adhd_mean_rand_pli[r, b, :] = np.mean(m, axis=0)
adhd_thres = np.amax(adhd_mean_rand_pli, axis=2)
nv_thres = np.amax(nv_mean_rand_pli, axis=2)

nv = np.zeros([5, 68])
adhd = np.zeros([5, 68])
for r in range(100):
    for b in range(5):
        m = mirror(meanNV[b, :, :])
        # m = np.ma.masked_equal(rand_nv[r, b, :, :], 0)
        nv[b, :] = np.mean(m, axis=0)
        m = mirror(meanADHD[b, :, :])
        adhd[b, :] = np.mean(m, axis=0)

nv_pvals = np.zeros_like(nv)
adhd_pvals = np.zeros_like(adhd)
for b in range(5):
    for l in range(68):
        nv_pvals[b, l] = np.sum(nv_thres[:, b] >= nv[b, l]) / 100.
        adhd_pvals[b, l] = np.sum(adhd_thres[:, b] >= adhd[b, l]) / 100.
