import mne
import pylab as pl
import numpy as np
import virtual_electrode as ve
import env
import find_good_segments as fgs
import glob
import spreadsheet
import os
from scipy import stats


def mirror(A):
    # makes A a mirror matrix (mirrowing the lower triangle)
    n = A.shape[0]
    A[np.triu_indices(n)] = A.T[np.triu_indices(n)]
    return A


def conn_profile(pli):
    # calculating connectivity profile
    conn_pf = []
    for b in range(pli.shape[1]):
        pf = np.zeros([pli.shape[0], pli.shape[2]])  # subjs x labels
        for s in range(pli.shape[0]):
            m = mirror(pli[s, b, :, :])
            pf[s, :] = stats.nanmean(m, axis=-1)
        conn_pf.append(pf)
    return conn_pf


def dmn_vs_rest(pf):
    dmnr = [51, 47, 15, 63, 29, 53]
    dmnl = [50, 46, 14, 62, 28, 52]
    dmn = np.concatenate((dmnl, dmnr))
    nondmn = range(68)
    nondmn = np.setdiff1d(nondmn, dmn)
    pvals = []
    for b in range(5):
        A = pf[b][:, nondmn].flatten()
        B = pf[b][:, dmn].flatten()
        t, p = stats.ttest_ind(A, B)
        pvals.append(p)
    return pvals


execfile('/Users/sudregp/research_code/combine_good_plis.py')

pcc = [50, 46, 51, 47]
par = [14, 62, 15, 63]
mpfc = [28, 52, 29, 53]

num_bands = 5

# let's go with Philip's suggestion and try to analyze within NV first, with the idea that PLI for DMN regions should be higher than non-DMN
nv_pf = conn_profile(nv)
adhd_pf = conn_profile(adhd)

nv_pvals = dmn_vs_rest(nv_pf)
adhd_pvals = dmn_vs_rest(adhd_pf)

pvals = []
for b in range(5):
    A = nv_pf[b][:, :].flatten()
    B = adhd_pf[b][:, :].flatten()
    t, p = stats.ttest_ind(A, B)
    pvals.append(p)

dmnl = [50, 46, 14, 62, 28, 52]
print "DMN (showing only L)"
for l in dmnl:
    print labels[l]


