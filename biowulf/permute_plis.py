import virtual_electrode as ve
import numpy as np
import multiprocessing
import env

job_num = int(multiprocessing.cpu_count())

num_perms = 2
num_bands = 5
num_labels = 68
rand_plis = np.zeros([num_perms, num_bands, num_labels, num_labels])

# Note that the voxels selected should stay the same because the pemrutation doesn't change the power, only the phase, but if we load it now we can speed it up later by forcing the voxels being chosen, and not having to do the power transform all the time
res = np.load(env.results + 'selected_voxels_NV.npz')
subj_voxels = res['subj_voxels'][()]

num_subj = len(subj_voxels.keys())
for r in range(num_perms):

    print '==================================='
    print '========  Permutation ' + str(r+1) + ' ==========='
    print '==================================='

    # construct the arrays that we'll average over. They need to be subj x band x labels x labels
    perm_plis = np.zeros([num_subj, num_bands, num_labels, num_labels])

    cnt = 0
    for subj, voxels in subj_voxels.iteritems():
        pli, labels, bands, junk = ve.compute_all_labels_pli(subj, rand_phase=True, selected_voxels=voxels, job_num=job_num)
        for band in range(num_bands):
            perm_plis[cnt, band, :, :] = pli[band]
        cnt += 1

    rand_plis[r, :, :, :] = np.mean(perm_plis, axis=0)

import time
np.savez(env.results + 'rand_plis_NV_' + str(int(time.time())), rand_plis=rand_plis)
