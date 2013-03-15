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

for subj, voxels in subj_voxels.iteritems():
    print '==================================='
    print '=======  Subject ' + subj + ' ========='
    print '==================================='
    pli, labels, bands, junk = ve.compute_all_labels_pli(subj, rand_phase=num_perms, selected_voxels=voxels, job_num=job_num)
