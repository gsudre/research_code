# script to match the behavior responses to the parsed MEg data
import mne
import numpy as np
import os
home = os.path.expanduser('~')

data_dir = '/mnt/neuro/MEG_data/analysis/stop/parsed/'
behavior_dir = '/mnt/Labs/Shaw/MEG_behavioral/clean_behavioral/Exported/'

subj = 'ABUTRIKQ'
delete_blocks = [8]

######## END of VARIABLES #########
new_event_ids = {'STB': 10, 'STG-correct': 11, 'STG-incorrect': 12,
                 'STI-correct': 13, 'STI-incorrect': 14}

fname = behavior_dir+'/%s_triaOrder.txt'%subj
fid = open(fname, 'r')
behavior = [line.rstrip() for line in fid]
fid.close()
fname = data_dir+'/%s_event_order.txt'%subj
fid = open(fname, 'r')
events = [line.rstrip() for line in fid]
fid.close()

epochs_fname = data_dir + subj + '_stop_parsed_DS300-epo.fif.gz'
epochs = mne.read_epochs(epochs_fname)

new_events = epochs.events.copy()
# check how many events match starting from the first one
cnt = 0
match = True
while cnt<min(len(behavior),len(events)) and match:
    match = behavior[cnt].find(events[cnt])>=0
    if match:
        new_events[cnt, 2] = new_event_ids[behavior[cnt]]
    cnt += 1
print 'Last matched event for %s: %d (Beh: %d, Eve: %d)'%(
    subj, cnt, len(behavior), len(events))

# saving changes to Epoch
epochs.event_id = new_event_ids
epochs.events = new_events

# make sure the blocks are in descending order so we don't screw up the deletion
delete_blocks.sort()
delete_blocks = delete_blocks[::-1]
for b in delete_blocks:
    idx = (b-1)*86 + np.arange(86)
    epochs.drop_epochs(idx)


print 'Saving to disk...'
epochs.save(data_dir + subj + '_stop_parsed_DS300_matched-epo.fif.gz')