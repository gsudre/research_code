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
import pdb


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
        A = np.mean(pf[b][:, nondmn], axis=-1)
        B = np.mean(pf[b][:, dmn], axis=-1)
        t, p = stats.ttest_ind(A, B)
        pvals.append(p)
    return pvals


def get_net_conn(pli, lidx):
    import itertools
    pairs = list(itertools.combinations(lidx, 2))
    conn = np.zeros([pli.shape[0], len(pairs)])
    for p, pair in enumerate(pairs):
        conn[:, p] = pli[:, pair[0], pair[1]]
    conn = stats.nanmean(conn, axis=-1)
    return conn


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
    A = np.mean(nv_pf[b][:, dmn], axis=-1)
    B = np.mean(adhd_pf[b][:, dmn], axis=-1)
    t, p = stats.ttest_ind(A, B)
    pvals.append(p)

dmnl = [50, 46, 14, 62, 28, 52]
print "DMN (showing only L)"
for l in dmnl:
    print labels[l]

# here we test the 7 networks in the Brookes 2011 paper (no cerebellum)
# nets is a list of networks, and bands is the band in each network
band_names = ['delta', 'theta', 'alpha', 'beta', 'gamma']
nets = [['medialorbitofrontal-lh', 'medialorbitofrontal-rh', 'rostralanteriorcingulate-lh', 'rostralanteriorcingulate-rh', 'inferiorparietal-lh', 'inferiorparietal-rh'],
        ['inferiorparietal-lh', 'superiorparietal-lh', 'supramarginal-lh', 'medialorbitofrontal-lh', 'rostralanteriorcingulate-lh'],
        ['inferiorparietal-rh', 'superiorparietal-rh', 'supramarginal-rh', 'medialorbitofrontal-rh', 'rostralanteriorcingulate-rh'],
        ['precentral-lh', 'precentral-rh', 'postcentral-lh', 'postcentral-rh'],
        ['supramarginal-lh', 'supramarginal-rh'],
        ['lateraloccipital-lh', 'lateraloccipital-rh'],
        ['medialorbitofrontal-lh', 'medialorbitofrontal-rh', 'rostralanteriorcingulate-lh', 'rostralanteriorcingulate-rh']]

bands = ['alpha', 'beta', 'beta', 'beta', 'beta', 'beta', 'beta', 'beta']

pvals2 = []
for n, net in enumerate(nets):
    # find index corresponding to band
    b = [b for b, band in enumerate(band_names) if band == bands[n]][0]
    # find index corresponding to labels
    lidx = []
    for net_label in net:
        l = [l for l, label in enumerate(labels) if label == net_label][0]
        lidx.append(l)
    nv_conn = get_net_conn(nv[:, b, :, :], lidx)
    adhd_conn = get_net_conn(adhd[:, b, :, :], lidx)
    pdb.set_trace()
    t, p = stats.ttest_ind(nv_conn, adhd_conn)
    pvals2.append(p)

