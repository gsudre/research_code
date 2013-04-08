import virtual_electrode as ve
import numpy as np
import env
import mne
import find_good_segments as fgs
import time

job_num = 1

num_perms = 20

# Note that the voxels selected should stay the same because the pemrutation doesn't change the power, only the phase, but if we load it now we can speed it up later by forcing the voxels being chosen, and not having to do the power transform all the time
res = np.load(env.results + 'selected_voxels_chl.5_lp58_hp.5.npz')
selected_voxels = res['selected_voxels'][()]
labels = res['labels'][()]
bands = res['bands'][()]

for subj, voxels in selected_voxels.iteritems():
    print '==================================='
    print '=======  Subject ' + subj + ' ========='
    print '==================================='

    raw_fname = env.data + '/MEG_data/fifs/' + subj + '_rest_LP100_CP3_DS300_raw.fif'
    fwd_fname = env.data + '/MEG_data/analysis/rest/' + subj + '_rest_LP100_CP3_DS300_raw-5-fwd.fif'

    # preloading makes computing the covariance a lot faster
    raw = mne.fiff.Raw(raw_fname, preload=True)
    fwd = mne.read_forward_solution(fwd_fname)

    epochs = fgs.crop_good_epochs(raw, threshold=3500e-15, allowed_motion=.5, fmin=.5, fmax=58)

    stcs = ve.localize_epochs(epochs, fwd, reg=0)

    rand_plis = np.zeros([num_perms, len(bands), len(labels[subj]), len(labels[subj])])
    for r in range(num_perms):
        print '==================================='
        print '========  Permutation ' + str(r+1) + ' ==========='
        print '==================================='
        pli = ve.compute_pli_epochs(stcs[:5], labels[subj], selected_voxels[subj], bands, randomize=True)
        for band in range(len(bands)):
            rand_plis[r, band, :, :] = pli[band]

    np.savez(env.results + 'rand_' + str(num_perms) + '_plis_' + subj + '_' + str(int(time.time())), rand_plis=rand_plis)
