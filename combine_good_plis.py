import mne
import pylab as pl
import numpy as np
import virtual_electrode as ve
import env
import find_good_segments as fgs
import glob
import spreadsheet
import os


def combine_data(subjs, labels, pli):
    num_bands = len(pli[pli.keys()[0]])
    num_labels = len(labels[labels.keys()[0]])
    comb_pli = np.empty([len(subjs), num_bands, num_labels, num_labels])
    comb_pli[:] = np.NaN
    for s, subj in enumerate(subjs):
        # for each subject, sort the labels by name and copy the data in the sorted order
        lnames = [l.name for l in labels[subj]]
        lorder = np.argsort(lnames)
        for l, label in enumerate(lorder):
            for b in range(num_bands):
                comb_pli[s, b, l, :] = pli[subj][b][label, :]
    lnames.sort()
    return comb_pli, lnames


res = env.load(env.results + 'good_plis_chl.5_lp58_hp.5_th3500e15_allsegs.npz')
adhd, labels = combine_data(list(res['good_adhds']), res['labels'], res['plis'])
nv, labels = combine_data(list(res['good_nvs']), res['labels'], res['plis'])
