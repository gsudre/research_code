# script to clean the task data using a combination of SSP and peak2peak rejection
import mne
import numpy as np
import glob
import os
import pylab as pl
home = os.path.expanduser('~')

subj = 'ETNOKHVP'
delete_blocks = []

epochs_dir = '/mnt/neuro/MEG_data/analysis/stop/parsed/'
evoked_dir = '/mnt/neuro/MEG_data/analysis/stop/evoked/'
raw_dir = '/mnt/neuro/MEG_data/fifs/stop/'

eog_chan = 'MLT41-1609'
conds = ['STG-correct', 'STI-correct', 'STB', 'STG-incorrect', 'STI-incorrect']

# figure out how many files the subject has
subj_files = glob.glob(raw_dir + subj + '*_BP1-35_raw.fif')
num_files = len(subj_files)
# always make the noise model based on the first session file
if num_files==1:
    raw_fname = raw_dir + '%s_stop_BP1-35_raw.fif'%subj
else:
    raw_fname = raw_dir + '%s_stop_s1_BP1-35_raw.fif'%subj
raw = mne.io.Raw(raw_fname, compensation=3, preload=True)
epochs_fname = epochs_dir + subj + '_stop_parsed_matched_BP1-35_DS120-epo.fif.gz'
epochs = mne.read_epochs(epochs_fname, proj=True)


# plotting raw data to check for any obvious noise
raw.plot()

# average 3 conditions for a better look at the data
data_chans = mne.pick_types(epochs.info,meg=True,ref_meg=False)
evokeds = [epochs[name].average() for name in conds[:3]]

# also do a comparative topoplot
colors = ['green', 'red', 'yellow']
title = 'Averaged data before EOG removal'
mne.viz.plot_topo(evokeds, color=colors, title=title)

# let's create SSP projectors for EOG:
proj, eog_events = mne.preprocessing.compute_proj_eog(raw, copy=True, ch_name=eog_chan,reject=None,n_mag=5)
layout = mne.find_layout(evokeds[0].info)
fig = pl.figure()
mne.viz.plot_projs_topomap(proj, layout=layout)

comps2use = raw_input('How many components to use? ')

# now we apply the recently created projections to our averaged data
epochs.add_proj(proj[:int(comps2use)], remove_existing=True)

# remove blocks that were crappy based on behavioral analysis
# make sure the blocks are in descending order so we don't screw up the deletion
delete_blocks.sort()
delete_blocks = delete_blocks[::-1]
for b in delete_blocks:
    idx = (b-1)*86 + np.arange(86) # 86 trails in each block
    epochs.drop_epochs(idx)

# let's apply the projections to a copy of the epochs, so that we can figure
# out which epochs can be dropped based on peak2peak, but avoid applying 
# the projections too early in the game. The problem is that because epochs was read from a fif, it doesn't have all the inherent properties (e.g. detrend, _raw_times and others). So, apply_proj() fails because it cannot preprocess the signal after applying the projections. Since we don't need to pre-process it, we can just apply the projections ourselves (copied from io/proj.py)
from copy import deepcopy
projector, info = mne.io.proj.setup_proj(deepcopy(epochs.info), activate=True)
epochs_tmp = epochs.copy()
old_data = epochs_tmp.get_data()
data = np.empty_like(old_data)
for ii, e in enumerate(old_data):
    data[ii] = np.dot(projector, e)
# got the threshold from Brainstorm (http://neuroimage.usc.edu/brainstorm/Tutorials/TutRawAvg, 2000 fT)
epochs_clean = mne.epochs.EpochsArray(data, info, epochs_tmp.events, reject=dict(mag=2e-12), event_id=epochs_tmp.event_id, tmin=np.min(epochs_tmp.times))

# and check how different the averages get
evokeds_clean = [epochs_clean[name].average() for name in conds[:3]]
title = 'Averaged data after EOG and bad trials removal'
mne.viz.plot_topo(evokeds_clean, color=colors, title=title)

# save evoked responses for all 5 conditions
print 'Saving evoked data...'
evokeds_clean = [epochs_clean[name].average() for name in conds]
mne.write_evokeds(evoked_dir + subj + '_stop_BP1-35_DS120-ave.fif', evokeds_clean)

# output number of averages
for ev in evokeds_clean:
    print ev.comment, ': %d averages'%ev.nave

# For the data tracker
print '=== Add to data tracker ==='
print 'Y\t%s\t%d\t%d\t%d'%(comps2use,evokeds_clean[1].nave,evokeds_clean[4].nave,evokeds_clean[0].nave) 
print '==============='

# now that we know which epochs to drop, copy the log to the actual epochs structure and drop them
bad_epochs = [i for i,j in enumerate(epochs_clean.drop_log) if len(j)>0]
epochs.drop_epochs(bad_epochs)
# save epochs with (optional) EOG projection
print 'Saving epochs with optional SSP operators...'
new_fname = epochs_dir + subj + '_stop_parsed_matched_clean_BP1-35_DS120-epo.fif.gz'
epochs.save(new_fname)