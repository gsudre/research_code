import mne
import pylab as pl
import numpy as np
import virtual_electrode as ve
import env
import find_good_segments as fgs
import os
import glob

bands = ([.5, 4], [4, 8])
res = np.load(env.results + 'good_epochs.npz')
subjs = res['subjs'][()]
good_segs = res['good_segs'][()]
plis = []
for s, subj in enumerate(subjs.keys()):
    if subjs[subj][0] == 'N' and good_segs[s] == 18:
        raw_fname = env.data + '/MEG_data/fifs/' + subj + '_rest_LP100_HP0.6_CP3_DS300_raw.fif'
        fwd_path = env.data + '/MEG_data/analysis/rest/'
        fwd_fname = fwd_path + subj + '_rest_LP100_HP0.6_CP3_DS300_raw-5-fwd.fif'

        # preloading makes computing the covariance a lot faster
        raw = mne.fiff.Raw(raw_fname, preload=True)
        fwd = mne.read_forward_solution(fwd_fname)

        epochs = fgs.find_good_epochs(raw, threshold=3500e-15)
        stcs = ve.localize_epochs(epochs, fwd, reg=0)

        labels_folder = os.environ['SUBJECTS_DIR'] + '/' + subj + '/labels/'
        label_names = glob.glob(labels_folder + '/*.label')

        print 'Reading subject labels...'
        labels = [mne.read_label(ln) for ln in label_names]

        # NEED TO CHANGE THIS TO CHOOSE VOXELS OVER ALL EPOCHS!
        selected_voxels = ve.find_best_voxels(stcs[0], labels, bands, 1)
        pli = ve.compute_pli_epochs(stcs, labels, None, bands)
        plis.append(pli)
