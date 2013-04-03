import mne
import numpy as np
import virtual_electrode as ve
import env
import find_good_segments as fgs
import os
import glob
import sys

res = np.load(env.results + 'intra_subj_stab.npz')
epoch_ids = res['epoch_ids'][()]
subjs = list(res['best_nvs'][()])
subj = subjs[int(sys.argv[1])]
num_rand_sets = len(epoch_ids)

bands = ([.5, 4], [4, 8])

raw_fname = env.data + '/MEG_data/fifs/' + subj + '_rest_LP100_CP3_DS300_raw.fif'
fwd_path = env.data + '/MEG_data/analysis/rest/'
fwd_fname = fwd_path + subj + '_rest_LP100_CP3_DS300_raw-5-fwd.fif'

# preloading makes computing the covariance a lot faster
raw = mne.fiff.Raw(raw_fname, preload=True)
fwd = mne.read_forward_solution(fwd_fname)

epochs = fgs.crop_good_epochs(raw, threshold=3500e-15, fmin=.5, fmax=58)
stcs = ve.localize_epochs(epochs, fwd, reg=0)

labels_folder = os.environ['SUBJECTS_DIR'] + '/' + subj + '/labels/'
label_names = glob.glob(labels_folder + '/*.label')

print 'Reading subject labels...'
labels = [mne.read_label(ln) for ln in label_names]

selected_voxels = ve.find_best_voxels_epochs(stcs, labels, bands, job_num=1)

plis = []
for r, rand_ids in enumerate(epoch_ids):
    print '\nRunning random set ' + str(r+1) + '/' + str(num_rand_sets)
    rnd_epochs = [stcs[epoch] for epoch in rand_ids]
    pli = ve.compute_pli_epochs(rnd_epochs, labels, selected_voxels, bands)
    plis.append(pli)

np.savez(env.results + subj + '_rand_epochs', subj=subj, plis=plis, bands=bands, epoch_ids=epoch_ids)
