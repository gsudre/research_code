''' Combines all resulting files from PLI permutations '''

import numpy as np
import glob
import env

num_perm = 200
perm_blocks = 5
num_bands = 5
num_labels = 68

res = np.load(env.results + 'selected_voxels_chl.5_lp58_hp.5_th3500e15.npz')
subj_voxels = res['selected_voxels'][()]
subjs = subj_voxels.keys()

num_subj = len(subjs)
rand_plis = {}
for s, subj in enumerate(subjs):
    print('Subject {}/{}').format(s + 1, num_subj)
    subj_rand_pli = np.empty([num_perm, num_bands, num_labels, num_labels])
    subj_rand_pli[:] = np.NaN
    rand_files = glob.glob(env.results + 'rand_' + str(perm_blocks) + '_plis_' + subj + '_*.npz')
    cnt = 0
    for file in rand_files:
        if cnt < num_perm:
            res = np.load(file)
            tmp = res['rand_plis'][()]
            subj_rand_pli[cnt:(cnt + perm_blocks), :, :, :] = tmp
            cnt += perm_blocks
    rand_plis[subj] = subj_rand_pli
