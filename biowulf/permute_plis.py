import virtual_electrode as ve
import numpy as np
import multiprocessing
import env

job_num = int(multiprocessing.cpu_count())

fid = open(env.maps + 'MEG_adults_good_ADHDs.txt', 'r')

# counting how many subjects we have
subjs = fid.readlines()

num_subj = 0
for subj in subjs:
    if subj.rstrip() > 0:
        num_subj += 1

num_perms = 2
num_bands = 5
num_labels = 68
rand_plis = np.zeros([num_perms, num_bands, num_labels, num_labels])


# let's do this once with the real data so that we can get the correct voxels. Note that the voxels selected should stay the same because the pemrutation doesn't change the power, only the phase, but if we do it now we can speed it up later by forcing the voxels being chosen, and not having to do the power transform all the time
subj_voxels = []
for ids, subj in enumerate(subjs):
    if subj.rstrip() > 0:
        pli, labels, bands, selected_voxels = ve.compute_all_labels_pli(subj.rstrip(), job_num=job_num)
        subj_voxels.append(selected_voxels)

for r in range(num_perms):

    print '==================================='
    print '========  Permutation ' + str(r+1) + ' ==========='
    print '==================================='

    # construct the arrays that we'll average over. They need to be subj x band x labels x labels
    perm_plis = np.zeros([num_subj, num_bands, num_labels, num_labels])

    for ids, subj in enumerate(subjs):
        if subj.rstrip() > 0:
            pli, labels, bands, junk = ve.compute_all_labels_pli(subj.rstrip(), rand_phase=True, selected_voxels=subj_voxels[ids], job_num=job_num)
            for band in range(num_bands):
                perm_plis[ids, band, :, :] = pli[band]

    rand_plis[r, :, :, :] = np.mean(perm_plis, axis=0)

fid.close()

import time
np.savez(env.results + 'rand_plis_ADHD_' + str(int(time.time())), rand_plis=rand_plis)
