''' Computes the PLI for the first 5 epochs for each good subject (i.e. more than 175s of good data) '''

import mne
import numpy as np
import virtual_electrode as ve
import env
import find_good_segments as fgs


res = np.load(env.results + 'num_clean_epochs_chl.5_lp58_hp.5_visual.npz')
data_mrks = res['markers'][()]
chl_mrks = res['chl_mrks'][()]
seg_len = res['seg_len'][()]

res = env.load(env.results + 'selected_voxels_all_chl.5_lp58_hp.5_visual.npz')
labels = res['labels']
selected_voxels = res['selected_voxels']
good_subjects = list(res['good_nvs']) + list(res['good_adhds'])

plis = {}

for subj in good_subjects:
    raw_fname = env.data + '/MEG_data/fifs/' + subj + '_rest_LP58_HP.5_CP3_DS300_raw.fif'
    fwd_fname = env.data + '/MEG_data/analysis/rest/' + subj + '_rest_LP100_CP3_DS300_raw-5-fwd.fif'

   # preloading makes computing the covariance a lot faster
    raw = mne.fiff.Raw(raw_fname, preload=True)
    fwd = mne.read_forward_solution(fwd_fname)
    _, times = raw[:, :]

    mrks = data_mrks[subj] + chl_mrks[subj]
    events = fgs.get_good_events(mrks, times, seg_len)
    epochs = fgs.crop_clean_epochs(raw, events, seg_len=seg_len)

    stcs = ve.localize_epochs(epochs, fwd, reg=0)

    plis[subj] = ve.compute_pli_epochs(stcs, labels[subj], selected_voxels[subj], res['bands'])

np.savez(env.results + 'good_plis_all_chl.5_lp58_hp.5_visual.npz', plis=plis)
