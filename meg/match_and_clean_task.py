# Script to borrow match of events and clean epochs/SSP vectors from BP1-35Hz pipeline to the epochs with higher frequencies
import mne
import os
home = os.path.expanduser('~')
import sys
import numpy as np


epochs_dir = '/mnt/shaw/MEG_data/analysis/stop/parsed/'
conds = ['STG-correct', 'STI-correct', 'STB', 'STG-incorrect', 'STI-incorrect']
evoked_dir = '/mnt/shaw/MEG_data/analysis/stop/evoked/'

if len(sys.argv) > 1:
    subj = sys.argv[1]
else:
    subj = 'ABUTRIKQ'

# open the matched BP1-35Hz file and borrow its event labels
epochs_fname = epochs_dir + subj + '_stop_parsed_matched_BP1-35_DS120-epo.fif.gz'
epochs35 = mne.read_epochs(epochs_fname, proj=True)
epochs_fname = epochs_dir + subj + '_stop_parsed_BP1-100_DS300-epo.fif.gz'
epochs = mne.read_epochs(epochs_fname, proj=True)
# we need to drop events that were not matched
if len(epochs35.events) < len(epochs.events):
    drop_me = np.arange(len(epochs.events))
    drop_me[drop_me < len(epochs35.events)] = 0
    drop_me = np.nonzero(drop_me)[0]
    epochs.drop_epochs(drop_me)
epochs.event_id = epochs35.event_id
epochs.events = epochs35.events

# open the cleaned epochs file and grab its SSP operators and clean log
epochs_fname = epochs_dir + subj + '_stop_parsed_matched_clean_BP1-35_DS120-epo.fif.gz'
epochs35 = mne.read_epochs(epochs_fname, proj=True)
bad_epochs = [i for i, j in enumerate(epochs35.drop_log) if len(j) > 0]
epochs.drop_epochs(bad_epochs)
epochs.info['projs'] = epochs35.info['projs']

# make averaged file and save final result
print 'Saving epochs and evoked data with optional SSP operators...'
evokeds = [epochs[name].average() for name in conds]
mne.write_evokeds(evoked_dir + subj + '_stop_parsed_matched_BP1-100_DS300-ave.fif', evokeds)
new_fname = epochs_dir + subj + '_stop_parsed_matched_clean_BP1-100_DS300-epo.fif.gz'
epochs.save(new_fname)
