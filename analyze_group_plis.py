import numpy as np
from scipy import stats
import env

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



