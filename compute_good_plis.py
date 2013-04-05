''' Computes the PLI for the first 5 epochs for each good subject (i.e. more than 175s of good data) '''

import mne
import numpy as np
import virtual_electrode as ve
import env
import find_good_segments as fgs
import glob
import spreadsheet
import os

bands = ([.5, 4], [4, 8], [8, 13], [13, 30], [30, 58])

res = np.load(env.results + 'good_epochs_chl.5_lp58_hp.5.npz')
good_epochs = res['good_epochs'][()]
adhds = spreadsheet.get_adults(True)
nvs = spreadsheet.get_adults(False)

good_nvs = [subj for subj, val in good_epochs.iteritems() if val > 13 and subj in nvs]
good_adhds = [subj for subj, val in good_epochs.iteritems() if val > 13 and subj in adhds]
good_subjects = good_nvs + good_adhds
plis = {}
selected_voxels = {}

for subj in good_subjects:
    raw_fname = env.data + '/MEG_data/fifs/' + subj + '_rest_LP100_CP3_DS300_raw.fif'
    fwd_fname = env.data + '/MEG_data/analysis/rest/' + subj + '_rest_LP100_CP3_DS300_raw-5-fwd.fif'
    labels_folder = os.environ['SUBJECTS_DIR'] + '/' + subj + '/labels/'

    # preloading makes computing the covariance a lot faster
    raw = mne.fiff.Raw(raw_fname, preload=True)
    fwd = mne.read_forward_solution(fwd_fname)

    epochs = fgs.crop_good_epochs(raw, threshold=3500e-15, allowed_motion=.5, fmin=.5, fmax=58)

    stcs = ve.localize_epochs(epochs, fwd, reg=0)

    label_names = glob.glob(labels_folder + '/*.label')

    print 'Reading subject labels...'
    labels = [mne.read_label(ln) for ln in label_names]

    selected_voxels[subj] = ve.find_best_voxels_epochs(stcs, labels, bands, job_num=1)

    plis[subj] = ve.compute_pli_epochs(stcs[:5], labels, selected_voxels[subj], bands)

np.savez(env.results + 'good_plis_chl.5_lp58_hp.5.npz', good_nvs=good_nvs, good_adhds=good_adhds, plis=plis, bands=bands)
np.savez(env.results + 'selected_voxels_chl.5_lp58_hp.5.npz', good_nvs=good_nvs, good_adhds=good_adhds, selected_voxels=selected_voxels, bands=bands)
