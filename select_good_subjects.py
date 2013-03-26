import find_good_segments as fgs
import spreadsheet
import numpy as np
import mne
import env

subjs = spreadsheet.get_all_subjects()

# using blocks, in the old code
good_segs = np.zeros([len(subjs)])
for ids, s in enumerate(subjs):
    start, end, num_chans = fgs.find_good_segments(s, threshold=3500e-15)
    good_segs[ids] = end - start

# using the new code, which finds epochs
good_epochs = {}
for subj in subjs.iterkeys():
    raw_fname = env.data + '/MEG_data/fifs/' + subj + '_rest_LP100_HP0.6_CP3_DS300_raw.fif'
    raw = mne.fiff.Raw(raw_fname)
    epochs = fgs.find_good_epochs(raw, threshold=3500e-15)
    if epochs is not None:
        good_epochs[subj] = epochs.get_data().shape[0]
    else:
        good_epochs[subj] = 0
