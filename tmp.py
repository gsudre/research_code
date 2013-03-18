import mne
import pylab as pl
import numpy as np
import test_pli_stability as tps

job_num = 1

fid = open(env.maps + 'MEG_adults_good_NVs.txt', 'r')

# counting how many subjects we have
subjs = fid.readlines()

num_subj = 0
for subj in subjs:
    if subj.rstrip() > 0:
        num_subj += 1

# let's do this once with the real data so that we can get the correct voxels. Note that the voxels selected should stay the same because the pemrutation doesn't change the power, only the phase, but if we do it now we can speed it up later by forcing the voxels being chosen, and not having to do the power transform all the time
subj_voxels = {}
for ids, subj in enumerate(subjs):
    if subj.rstrip() > 0:
        pli, labels, bands, selected_voxels = ve.compute_all_labels_pli(subj.rstrip(), job_num=job_num)
        subj_voxels[subj.rstrip()] = selected_voxels