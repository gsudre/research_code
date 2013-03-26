import mne
import numpy as np
import virtual_electrode as ve
import env
import find_good_segments as fgs
import os
import glob

num_rand_sets = 3
num_good_epochs = 7
num_epochs_to_run = 5
epoch_ids = []
for r in range(num_rand_sets):
    # because we have all good segments
    epoch_ids.append(np.random.permutation(num_good_epochs)[:num_epochs_to_run])

bands = ([.5, 4], [4, 8])
# res = np.load(env.results + 'good_epochs.npz')
# subjs = res['subjs'][()]
# good_segs = res['good_segs'][()]
subj = 'VWEJZSBN'

raw_fname = env.data + '/MEG_data/fifs/' + subj + '_rest_LP100_CP3_DS300_raw.fif'
fwd_path = env.data + '/MEG_data/analysis/rest/'
fwd_fname = fwd_path + subj + '_rest_LP100_CP3_DS300_raw-5-fwd.fif'

# preloading makes computing the covariance a lot faster
raw = mne.fiff.Raw(raw_fname, preload=True)
fwd = mne.read_forward_solution(fwd_fname)

epochs = fgs.find_good_epochs(raw, threshold=3500e-15)
stcs = ve.localize_epochs(epochs, fwd, reg=0)

labels_folder = os.environ['SUBJECTS_DIR'] + '/' + subj + '/labels/'
label_names = glob.glob(labels_folder + '/*.label')

print 'Reading subject labels...'
labels = [mne.read_label(ln) for ln in label_names]

selected_voxels = ve.find_best_voxels_epochs(stcs, labels, bands, job_num=1)

plis = []
for rand_ids in epoch_ids:
    print '\nRunning random set ' + str(r+1) + '/' + str(num_rand_sets)
    rnd_epochs = [stcs[epoch] for epoch in rand_ids]
    pli = ve.compute_pli_epochs(rnd_epochs, labels, selected_voxels, bands)
    plis.append(pli)

np.savez(env.results + subj + '_rand_epochs', subj=subj, plis=plis, bands=bands, epoch_ids=epoch_ids)
