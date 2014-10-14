import mne
import numpy as np
import glob


data_dir = '/mnt/neuro/MEG_data/fifs/stop/'
dir_out = '/mnt/neuro/MEG_data/analysis/stop/parsed/'
# with respect to begin of fixation
tmin = -.5
tmax = 1.5

# subjs_fname = home+'/data/meg/usable_subjects_5segs13p654.txt'
# fid = open(subjs_fname, 'r')
# subjs = [line.rstrip() for line in fid]

subjs = ['GOMPBCFD']

for subj in subjs:
    # figure out how many files the subject has
    subj_files = glob.glob(data_dir + subj + '*_raw.fif')
    num_files = len(subj_files)
    for f in range(num_files):
        if num_files==1:
            raw_fname = data_dir + '%s_stop_raw.fif'%subj
        else:
            raw_fname = data_dir + '%s_stop_s%_raw.fif'%(subj,f+1)
        raw = mne.fiff.Raw(raw_fname, compensation=3)
        events = mne.find_events(raw, stim_channel='UPPT001', consecutive=True, min_duration=.1)
        # shift the start sample so that 0 is 500ms before, where the fixation cross came up
        events[:,0] = events[:,0] - .5 * raw.info['sfreq']
        # there's a delay between trigger and visual cue of about 74ms
        events[:,0] = events[:,0] + .075 * raw.info['sfreq']

        # X and O are 1 and 3 (or vice-versa). If followed by a 2, it's STG. If followed by a 4, it's STI. If 0 goes to 5, it's STB. Also, note that if it's STG, the X/O stays up always for 1s, then the 2 comes up. STIs are more variable based on the subject's performance.
        filtered_events = []
        # start in the first example that starts at 0
        cnt = np.nonzero(events[:,1]==0)[0][0]
        # in filtered events, STG=1, STI=3, STB=5
        event_order = [] # will be written later to a text file
        # assuming that the events come in pairs
        while cnt < events.shape[0]-1:
            if ((events[cnt,2]==1) and (events[cnt+1,2]==2)) or (
                (events[cnt,2]==3) and (events[cnt+1,2]==2)):
                filtered_events.append(np.array([events[cnt,0],0,1]))
                event_order.append('STG')
            elif ((events[cnt,2]==1) and (events[cnt+1,2]==4)) or (
                (events[cnt,2]==3) and (events[cnt+1,2]==4)):
                filtered_events.append(np.array([events[cnt,0],0,3]))
                event_order.append('STI')
            elif events[cnt,2]==5:
                filtered_events.append(np.array([events[cnt,0],0,5]))
                event_order.append('STB')
            cnt += 1
        filtered_events = np.array(filtered_events)

        event_id = {'STG': 1, 'STI':3, 'STB': 5}
        if f==0:
            epochs = mne.Epochs(raw, filtered_events, event_id, tmin, tmax,
                    baseline=(None, 0), proj=False, preload=True)
        else:
            epochs2 = mne.Epochs(raw, filtered_events, event_id, tmin, tmax,
                    baseline=(None, 0), proj=False, preload=True)
            epochs = epochs + epochs2
    epochs.resample(300)
    epochs.save(dir_out + subj + '_stop_parsed_DS300_raw.fif')
    fid = open(dir_out + subj + '_event_order.txt','w')
    for ev in event_order:
        fid.write(ev + '\n')
    fid.close()




