''' Script to save the number of clean epochs for each subject '''

import find_good_segments as fgs
import mne
import env
import numpy as np

seg_len = 13.66  # corresponds to 4096 samples in our sampling rate of 300Hz

# subjects for which to get the data, but don't check for CHL
no_chl_subjs = ['GYURGRWX', 'INSJTGTJ', 'BPPPDMXT', 'ILUVLFGJ',
                'ZKNUZRLN', 'JILJXPMM', 'KXVGYZMK', 'ZILYTPUL',
                'WHPYSIQL', 'CMAOTMDG', 'AQBNNQMR', 'LDPZODZI',
                'FHPHIIQJ', 'EQMSSLGP', 'JZFEBOBR']
# don't use these subjects regardless of what's in the data, based on observations during the scan
bad_subjs = ['XKSKEASF', 'RELHQPFH', 'HUKEPSWW']

markers = fgs.read_marker_files()
num_clean_epochs = {}
chl_mrks = {}
for subj, mrks in markers.iteritems():
    # note that here we look at the version of FIFF without HP, because the filter screws up the position channels!
    fid = env.data + '/MEG_data/fifs/' + subj + '_rest_LP100_CP3_DS300_raw.fif'
    raw = mne.fiff.Raw(fid, preload=True)
    _, times = raw[:, :]
    if subj not in no_chl_subjs:
        print 'Checking CHL...'
        chl_mrks[subj] = fgs.read_chl_events(raw, times)
        mrks = mrks + chl_mrks[subj]
    else:
        chl_mrks[subj] = []

    events = fgs.get_good_events(mrks, times, seg_len)
    if len(events) == 0 or subj in bad_subjs:
        num_clean_epochs[subj] = 0
    else:
        epochs = fgs.crop_clean_epochs(raw, events, seg_len=seg_len)
        num_clean_epochs[subj] = epochs.get_data().shape[0]

np.savez(env.results + 'num_clean_epochs_chl.5_lp58_hp.5_visual', num_clean_epochs=num_clean_epochs, markers=markers, chl_mrks=chl_mrks, seg_len=seg_len)
