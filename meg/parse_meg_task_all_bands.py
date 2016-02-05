import mne
import numpy as np
import glob
import os
home = os.path.expanduser('~')
import sys

data_dir = '/mnt/shaw/MEG_data/fifs/stop/'
dir_out = '/mnt/shaw/MEG_data/analysis/stop/parsed/'
# with respect to begin of fixation
tmin = -.5
tmax = 1.5

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
                filtered_events.append(np.array([events[cnt, 0], 0, 3]))
                event_order.append('STI')
            elif events[cnt, 2] == 5:
                filtered_events.append(np.array([events[cnt, 0], 0, 5]))
                event_order.append('STB')
            cnt += 1
        filtered_events = np.array(filtered_events)

        # filtering raw to remove breathing artifacts and stuff we won't need
        # for evoked analysis. Do it here because mne_process_raw wipes out
        # events channel
        raw.filter(1, 100)
        # raw_fname2 = raw_fname.replace('raw', 'BP1-100_raw')
        # raw.save(raw_fname2, overwrite=True)

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

print 'Downsampling %s...' % subj
epochs.resample(300)
print 'Saving to disk...'
epochs.save(dir_out + subj + '_stop_parsed_BP1-100_DS300-epo.fif.gz')
# fid = open(dir_out + subj + '_event_order.txt','w')
# for ev in event_order:
#     fid.write(ev + '\n')
# fid.close()
