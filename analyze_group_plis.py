import numpy as np
import virtual_electrode as ve

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

    return mean_pli, std_pli

meanNV, stdNV = summarize_data(plis, '/Users/sudregp/results/good_NVs.txt')
meanADHD, stdADHD = summarize_data(plis, '/Users/sudregp/results/good_ADHDs.txt')

