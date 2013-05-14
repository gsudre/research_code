''' Selects the bext voxels based on power for all epochs for each good subject (i.e. more than 175s of good data) '''

import mne
import numpy as np
import virtual_electrode as ve
import env
import find_good_segments as fgs
import glob
import os

bands = ([.5, 4], [4, 8], [8, 13], [13, 30], [30, 58])
res = np.load(env.results + 'num_clean_epochs_chl.5_lp58_hp.5_visual.npz')

good_epochs = res['num_clean_epochs'][()]
data_mrks = res['markers'][()]
chl_mrks = res['chl_mrks'][()]
seg_len = res['seg_len'][()]
adhds = [line.strip() for line in open(env.tmp + 'adult_adhd.txt', 'r')]
nvs = [line.strip() for line in open(env.tmp + 'adult_nv.txt', 'r')]

good_nvs = [subj for subj, val in good_epochs.iteritems() if val > seg_len and subj in nvs]
good_adhds = [subj for subj, val in good_epochs.iteritems() if val > seg_len and subj in adhds]
good_subjects = good_nvs + good_adhds
selected_voxels = {}
# we had to save the labels as well because the order in which the labels are loaded changes between Mac and Linux, and we need the order to be constant for the selected_voxels matrix
labels = {}

for subj in good_subjects:
    raw_fname = env.data + '/MEG_data/fifs/' + subj + '_rest_LP58_HP.5_CP3_DS300_raw.fif'
    fwd_fname = env.data + '/MEG_data/analysis/rest/' + subj + '_rest_LP100_CP3_DS300_raw-5-fwd.fif'
    labels_folder = os.environ['SUBJECTS_DIR'] + '/' + subj + '/labels/'

    # preloading makes computing the covariance a lot faster
    raw = mne.fiff.Raw(raw_fname, preload=True)
    fwd = mne.read_forward_solution(fwd_fname)
    _, times = raw[:, :]

    mrks = data_mrks[subj] + chl_mrks[subj]
    events = fgs.get_good_events(mrks, times, seg_len)
    epochs = fgs.crop_clean_epochs(raw, events, seg_len=seg_len)

    stcs = ve.localize_epochs(epochs, fwd, reg=0)

    label_names = glob.glob(labels_folder + '/*.label')

    print 'Reading subject labels...'
    labels[subj] = [mne.read_label(ln) for ln in label_names]

    selected_voxels[subj] = ve.find_best_voxels_epochs(stcs, labels[subj], bands, job_num=1)


np.savez(env.results + 'selected_voxels_all_chl.5_lp58_hp.5_visual.npz', good_nvs=good_nvs, good_adhds=good_adhds, selected_voxels=selected_voxels, bands=bands, labels=labels, seg_len=seg_len)
