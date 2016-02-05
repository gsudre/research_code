import mne
import numpy as np
import glob
import os
home = os.path.expanduser('~')
import sys

data_dir = '/mnt/shaw/MEG_data/fifs/stop/'
dir_out = '/mnt/shaw/MEG_data/analysis/stop/parsed_red/'
clean_dir = '/mnt/shaw/MEG_data/analysis/stop/parsed/'
behavior_dir = '/mnt/shaw/MEG_behavioral/clean_behavioral/Exported/'
# with respect to begin of red square
tmin = -.5
tmax = 1

if len(sys.argv) > 1:
    subj = sys.argv[1]
else:
    subj = 'GOMPBCFD'

event_order = []

# figure out how many files the subject has
subj_files = glob.glob(data_dir + subj + '*_raw.fif')
# remove the band passed fif files
subj_files = [f for f in subj_files if f.find('_BP') < 0]
num_files = len(subj_files)
for f in range(num_files):
    if num_files == 1:
        raw_fname = data_dir + '%s_stop_raw.fif' % subj
    else:
        raw_fname = data_dir + '%s_stop_s%d_raw.fif' % (subj, f + 1)
    print raw_fname
    if os.path.exists(raw_fname):
        raw = mne.io.Raw(raw_fname, compensation=3, preload=True)
        events = mne.find_events(raw, stim_channel='UPPT001', consecutive=True, min_duration=.1)
        # shift the start sample so that 0 is 500ms before, where the fixation cross came up
        events[:, 0] = events[:, 0] - .5 * raw.info['sfreq']
        # there's a delay between trigger and visual cue of about 74ms
        events[:, 0] = events[:, 0] + .075 * raw.info['sfreq']

        # X and O are 1 and 3 (or vice-versa). If followed by a 2, it's STG. If followed by a 4, it's STI. If 0 goes to 5, it's STB. Also, note that if it's STG, the X/O stays up always for 1s, then the 2 comes up. STIs are more variable based on the subject's performance.
        filtered_events = []
        # start in the first example that starts at 0
        cnt = np.nonzero(events[:, 1] == 0)[0][0]
        # in filtered events, STG=1, STI=3, STB=5
        # assuming that the events come in pairs
        while cnt < events.shape[0]-1:
            if ((events[cnt, 2] == 1) and (events[cnt + 1, 2] == 2)) or (
               (events[cnt, 2] == 3) and (events[cnt + 1, 2] == 2)):
                filtered_events.append(np.array([events[cnt, 0], 0, 1]))
                event_order.append('STG')
            elif events[cnt + 1, 2] == 4:
                # because we'll only be interested in STI events later, 
                # we get the start of the red square. Also, I checked and
                # trigger 4 is variable with respect to 1 and 3, so we're
                # fine
                filtered_events.append(np.array([events[cnt + 1, 0], 0, 3]))
                event_order.append('STI')
            elif events[cnt, 2] == 5:
                filtered_events.append(np.array([events[cnt, 0], 0, 5]))
                event_order.append('STB')
            cnt += 1
        filtered_events = np.array(filtered_events)

        # we need to keep all events at this point because we'll need them
        # in the correct order in order to match with behavior

        # filtering raw to remove breathing artifacts and stuff we won't need
        # for evoked analysis. Do it here because mne_process_raw wipes out
        # events channel
        raw.filter(1, 100)

        if f > 0:
            all_events = mne.concatenate_events([all_events, filtered_events], [all_raw.first_samp, raw.first_samp], [all_raw.last_samp, raw.last_samp])
            all_raw = mne.concatenate_raws([all_raw, raw])
        else:
            all_raw = raw
            all_events = filtered_events

event_id = {'STG': 1, 'STI': 3, 'STB': 5}
picks = mne.pick_types(raw.info, meg=True, ref_meg=True)
epochs = mne.Epochs(all_raw, all_events, event_id, tmin, tmax,
                    baseline=(None, 0), proj=False, preload=True, picks=picks)

print subj
print epochs

# checking that we have at least 8 blocks of data
if np.sum(epochs.events[:, 2] == 1) < 352:
    print '\nERROR: Unexpected number of STG trials!'
    raw_input('Waiting for input...')
if np.sum(epochs.events[:, 2] == 3) < 160:
    print '\nERROR: Unexpected number of STI trials!'
    raw_input('Waiting for input...')
if np.sum(epochs.events[:, 2] == 5) < 176:
    print '\nERROR: Unexpected number of STB trials!'
    raw_input('Waiting for input...')

# match MEG data to behavioral so we can properly classify between STI correct
# and incorrect
new_event_ids = {'STG-correct': 11, 'STG-incorrect': 12,
                 'STI-correct': 13, 'STI-incorrect': 14, 'STB': 15}

if len(event_order) > 688:
    fname = behavior_dir + '/%s_m_triaOrder.txt' % subj
else:
    fname = behavior_dir + '/%s_triaOrder.txt' % subj
fid = open(fname, 'r')
behavior = [line.rstrip() for line in fid]
fid.close()

new_events = epochs.events.copy()
# check how many events match starting from the first one
cnt = 0
match = True
while cnt < min(len(behavior), len(event_order)) and match:
    match = behavior[cnt].find(event_order[cnt]) >= 0
    if match:
        new_events[cnt, 2] = new_event_ids[behavior[cnt]]
    cnt += 1
print 'Last matched event for %s: %d (Beh: %d, Eve: %d)' % (
    subj, cnt, len(behavior), len(event_order))

# saving changes to Epoch
epochs.event_id = new_event_ids
epochs.events = new_events

print 'Downsampling %s...' % subj
epochs.resample(300)

# let's save a version without dropping based on SSPs
red_epochs = epochs.copy()
no_interest = np.nonzero(red_epochs.events[:, 2] < 13)[0]
red_epochs.drop_epochs(no_interest)
print 'Saving epochs and evoked data...'
evokeds = [red_epochs[name].average() for name in ['STI-correct', 'STI-incorrect']]
mne.write_evokeds(dir_out + subj + '_stop_parsed_matched_BP1-100_DS300-ave.fif', evokeds)
new_fname = dir_out + subj + '_stop_parsed_matched_BP1-100_DS300-epo.fif.gz'
red_epochs.save(new_fname)

# now we save a version after cleaning with SSPs
# grab SSP vectors from previous cleanup sessions
epochs_fname = clean_dir + subj + '_stop_parsed_matched_clean_BP1-35_DS120-epo.fif.gz'
epochs35 = mne.read_epochs(epochs_fname, proj=True)
bad_epochs = [i for i, j in enumerate(epochs35.drop_log) if len(j) > 0]
epochs.drop_epochs(bad_epochs)
epochs.info['projs'] = epochs35.info['projs']

# removing the epochs we don't want, need to do it again because indices
# changed after removing bad epochs based on SSP
no_interest = np.nonzero(epochs.events[:, 2] < 13)[0]
epochs.drop_epochs(no_interest)

# make averaged file and save final result
print 'Saving epochs and evoked data with optional SSP operators...'
evokeds = [epochs[name].average() for name in ['STI-correct', 'STI-incorrect']]
mne.write_evokeds(dir_out + subj + '_stop_parsed_matched_clean_BP1-100_DS300-ave.fif', evokeds)
new_fname = dir_out + subj + '_stop_parsed_matched_clean_BP1-100_DS300-epo.fif.gz'
epochs.save(new_fname)
