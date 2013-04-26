import mne
import pylab as pl
import numpy as np
import virtual_electrode as ve
import env
import find_good_segments as fgs
import glob
import spreadsheet
import os


def mirror(A):
    # makes A a mirror matrix (mirrowing the lower triangle)
    n = A.shape[0]
    A[np.triu_indices(n)] = A.T[np.triu_indices(n)]
    return A


def combine_data(subjs, labels, pli):
    # combines the data into a big subj x band x roi x roi mirrored matrix
    num_bands = len(pli[pli.keys()[0]])
    num_labels = len(labels[labels.keys()[0]])
    comb_pli = np.empty([len(subjs), num_bands, num_labels, num_labels])
    comb_pli[:] = np.NaN
    for s, subj in enumerate(subjs):
        # for each subject, sort the labels by name and copy the data in the sorted order
        lnames = [l.name for l in labels[subj]]
        lorder = np.argsort(lnames)
        for b in range(num_bands):
            M = mirror(pli[subj][b][:, :])
            for l, label in enumerate(lorder):
                for l2, label2 in enumerate(lorder):
                    comb_pli[s, b, l, l2] = M[label, label2]
    lnames.sort()
    return comb_pli, lnames


def organize_random(plis, labels):
    # Mirrors a set of random plis
    num_bands = plis[plis.keys()[0]].shape[1]
    num_perms = plis[plis.keys()[0]].shape[0]
    sorted_plis = {}
    for subj, pli in plis.iteritems():
        # for each subject, sort the labels by name and copy the data in the sorted order
        lnames = [l.name for l in labels[subj]]
        lorder = np.argsort(lnames)

        comb_pli = np.empty_like(plis[subj])
        comb_pli[:] = np.NaN
        for b in range(num_bands):
            for p in range(num_perms):
                M = mirror(plis[subj][p, b, :, :])
                for l, label in enumerate(lorder):
                    for l2, label2 in enumerate(lorder):
                        comb_pli[p, b, l, l2] = M[label, label2]
        sorted_plis[subj] = comb_pli
    lnames.sort()
    return sorted_plis, lnames


def get_null_distributions(plis):
    # returns a null distribution per subject x band that is computed taking the mean over ROIs. Format is dict['subj'][perms x bands]

    rplis = {}
    for subj, data in plis.iteritems():
        rplis[subj] = np.nanmax(stats.nanmean(data, axis=-1), axis=-1)
    return rplis


res = env.load(env.results + 'good_plis_chl.5_lp58_hp.5_th3500e15_allsegs.npz')
adhd, labels = combine_data(list(res['good_adhds']), res['labels'], res['plis'])
nv, labels = combine_data(list(res['good_nvs']), res['labels'], res['plis'])
