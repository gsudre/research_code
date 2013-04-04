''' Combines all resulting files from testing intra-subject stability '''

import numpy as np
import glob
import env

num_perm = 100
num_bands = 2
num_labels = 68

rand_files = glob.glob(env.results + '*_rand_epochs.npz')
num_subj = len(rand_files)
rand_plis = np.zeros([num_subj, num_perm, num_bands, num_labels, num_labels])
cnt = 0
for f, fid in enumerate(rand_files):
    res = np.load(fid)
    plis = res['plis'][()]
    rand_plis[f, :, :, :, :] = plis
