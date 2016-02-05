# script to match the behavior responses to the parsed MEg data
import mne
import numpy as np
import os
home = os.path.expanduser('~')
import sys

data_dir = '/mnt/shaw/MEG_data/analysis/stop/parsed/'
behavior_dir = '/mnt/shaw/MEG_behavioral/clean_behavioral/Exported/'

if len(sys.argv) > 1:
    subj = sys.argv[1]
else:
    subj = 'ABUTRIKQ'

######## END of VARIABLES #########
new_event_ids = {'STB': 10, 'STG-correct': 11, 'STG-incorrect': 12,
                 'STI-correct': 13, 'STI-incorrect': 14}

fname = data_dir+'/%s_event_order.txt' % subj
fid = open(fname, 'r')
events = [line.rstrip() for line in fid]
fid.close()

if len(events) > 688:
    fname = behavior_dir+'/%s_m_triaOrder.txt' % subj
else:
    fname = behavior_dir+'/%s_triaOrder.txt' % subj
fid = open(fname, 'r')
behavior = [line.rstrip() for line in fid]
fid.close()

epochs_fname = data_dir + subj + '_stop_parsed_BP1-100_DS300-epo.fif.gz'
epochs = mne.read_epochs(epochs_fname)

new_events = epochs.events.copy()
# check how many events match starting from the first one
cnt = 0
match = True
while cnt < min(len(behavior), len(events)) and match:
    match = behavior[cnt].find(events[cnt]) >= 0
    if match:
        new_events[cnt, 2] = new_event_ids[behavior[cnt]]
    cnt += 1
print 'Last matched event for %s: %d (Beh: %d, Eve: %d)' % (
    subj, cnt, len(behavior), len(events))

# we need to drop events that were not matched
if len(behavior) < len(events):
    drop_me = np.arange(len(events))
    drop_me[drop_me < len(behavior)] = 0
    drop_me = np.nonzero(drop_me)[0]
    epochs.drop_epochs(drop_me)
    new_events = np.delete(new_events, drop_me, axis=0)

# saving changes to Epoch
epochs.event_id = new_event_ids
epochs.events = new_events

print 'Saving to disk...'
epochs.save(data_dir + subj + '_stop_parsed_matched_BP1-100_DS300-epo.fif.gz')
