# Function to find segment of good data in resting study
# by Gustavo Sudre, March 2013
import mne
import numpy as np
import env
import head_motion as hm
import pdb


def group_consecutives(vals, step=1):
    """Return list of consecutive lists of numbers from vals (number list)."""
    run = []
    result = [run]
    expect = None
    for v in vals:
        if (v == expect) or (expect is None):
            run.append(v)
        else:
            run = [v]
            result.append(run)
        expect = v + step
    return result


def find_good_segments(subj, data_path=env.data+'/MEG_data/fifs/',
                       threshold=4000e-13, window=5, good_chan_limit=250):

    raw_fname = data_path + subj + '_rest_LP100_HP0.6_CP3_DS300_raw.fif'
    raw = mne.fiff.Raw(raw_fname, preload=True)
    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')

    ''' The algorithm is quite simple: think of the signal as a matrix
    of channels x time, where time consists of windows of 1s. This
    matrix is boolean, based on wehther that time period crossed the
    threshold. Then, we add over the channels, and look for how many
    consecutive time windows had the score equal to the number of
    channels. '''

    data, time = raw[picks, :]
    num_windows = np.floor((time[-1] - time[0]) / window)
    good_chunk = np.zeros([data.shape[0], num_windows])
    time_window_start = []
    cur = 0
    for w in range(int(num_windows)):
        index = raw.time_as_index([cur, cur + window])
        time_window_start.append(cur)
        cur = cur + window
        chunk = data[:, index[0]:index[1]]
        peak2peak = abs(np.amax(chunk, axis=1) - np.amin(chunk, axis=1))
        good_chunk[:, w] = peak2peak < threshold
    good_chunk = np.sum(good_chunk, axis=0)

    best_seq_len = 0
    best_seq = [0]  # just so we can return something
    num_good_channels = len(picks)
    while best_seq_len <= 1 and num_good_channels >= good_chan_limit:
        # check which time windows had all channels being good
        good_windows = np.nonzero(good_chunk == num_good_channels)

        good_cons_windows = group_consecutives(good_windows[0])
        for s in good_cons_windows:
            if len(s) > best_seq_len:
                best_seq_len = len(s)
                best_seq = s

        if best_seq_len <= 1:
            num_good_channels -= 1

    if num_good_channels < good_chan_limit:
        print 'Hit minimum number of allowed bad channels. Stopping.\n'
    else:
        # formatting the output
        print 'Longest window: {}s ({} to {}), {} channels\n'.format(
            best_seq_len * window, time_window_start[best_seq[0]],
            time_window_start[best_seq[-1]] + window, num_good_channels)

    return (time_window_start[best_seq[0]],
            time_window_start[best_seq[-1]] + window, num_good_channels)


def crop_good_epochs(raw, window_length=13, step_length=1, threshold=4000e-13, allowed_motion=-1, verbose=1, fmin=0, fmax=np.Inf):
    ''' Returns an Epochs structure with what time periods to use. window_length and step_length are in seconds. Set allowed_motion to < 0 to avoid checking head position. '''

    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    # pdb.set_trace()
    # note that we need to filter raw, so that we can pass it on later
    if fmin > 0 and fmax < np.Inf:
        # bandpass the signal accordingly
        for s in picks:
            raw[s, :] = mne.filter.band_pass_filter(raw[s, :][0], raw.info['sfreq'], fmin, fmax, l_trans_bandwidth=.25)
    elif fmax < np.Inf:
        for s in picks:
            raw[s, :] = mne.filter.low_pass_filter(raw[s, :][0], raw.info['sfreq'], fmax)
    elif fmin > 0:
        for s in picks:
            raw[s, :] = mne.filter.high_pass_filter(raw[s, :][0], raw.info['sfreq'], fmin, trans_bandwidth=.25)

    ''' We search for windows of the given length. If a good window is found, add it to the list and check the next window (non-overlapping). If the current window is no good, step to the next available window. '''

    # # if there's no CHL, discard the subject right away
    # if hm.get_head_motion(raw) is None:
    #     return None

    events = []
    cur = 0
    window_size = int(window_length * raw.info['sfreq'])
    step_size = int(step_length * raw.info['sfreq'])
    while cur + window_size < raw.n_times:
        chunk = raw[picks, cur:(cur + window_size)][0]
        peak2peak = abs(np.amax(chunk, axis=1) - np.amin(chunk, axis=1))
        num_good_channels = np.sum(peak2peak < threshold, axis=0)
        # We can either completely disregard head position markers
        if allowed_motion < 0:
            max_motion = -np.Inf
        # if we're using them, check if the subject actually has them first
        elif hm.get_head_motion(raw) is not None:
            max_motion = hm.get_max_motion(raw, smin=cur, smax=(cur + window_size))
        # if the subject doesn't have them, return right away
        else:
            return None
        # print str(max_motion)
        # if all channels have p2p smaller than threshold, check head movement
        if num_good_channels == len(picks) and max_motion < allowed_motion:
            events.append([cur, 0, 0])
            cur += window_size
        else:
            cur += step_size

    print 'Found ' + str(len(events)) + ' good epochs (' + str(len(events)*window_length) + ' sec).'

    if len(events) > 0:
        events = np.array(events)
        epochs = mne.Epochs(raw, events, None, 0, window_length, keep_comp=True, preload=True, baseline=None, detrend=0, picks=picks)
    else:
        epochs = None

    return epochs


def read_marker_files(dataDir='/Volumes/neuro/MEG_data/raw/'):
    ''' Reads in all the markers form the ds raw data. Returns a list with markers for each subject in a dictionary. Each item in the dict is a list of timepoints, where odd items mark the time point where the bad segment started, and even numbers where they ended. '''

    import glob
    import os

    dates = glob.glob(dataDir + '/*')
    markers = {}
    for date in dates:
        # figure out the datasets with resting markers
        restF = glob.glob(date + '/*rest*-f.ds')
        # we assume that we only have one -f file per subject!
        for dsname in restF:
            # figuring out subject code
            ds_name = dsname.split('/')[-1]
            subj_code = ds_name.split('_')[0]

            # open Marker file if it exists
            if os.path.isfile(dsname + '/MarkerFile.mrk'):
                fid = open(dsname + '/MarkerFile.mrk')
                lines_list = fid.readlines()
                # finding the lines with markers
                mrk_lines = [line for line in lines_list if line.find('+0') > 0]

                # figure out what to do based on how many markers were found for subject!
                if len(mrk_lines) == 1:
                    print dsname + ' only has 1 marker: old -f?'
                elif len(mrk_lines) % 2 == 1:
                    print dsname + ' has odd number of markers!'
                else:
                    # check if we already have that subject
                    my_key = subj_code
                    if markers.has_key(my_key):
                        my_key = '%s_%03d'%(subj_code,np.random.randint(100))
                    # if we have an even number of events, collect them
                    markers[my_key] = [float(line.split()[-1]) for line in mrk_lines]
                    print dsname + ': ' + str(len(markers[my_key])) + ' markers'
    return markers


def get_good_events(markers, time, seg_len):
    ''' Returns a matrix of events in MNE style marking the segments of good data. Receives markers (list with markers for artifacts), time (array with time vector), and seg_len (how many seconds in each block). '''

    time_step = time[1] - time[0]
    sfreq = 1. / time_step
    sample_size = seg_len * sfreq

    # first, we remove from the time vector all the bad segments
    original_time = time
    cur_event = 0
    while cur_event < len(markers):
        index = (time < markers[cur_event]) | (time > markers[cur_event + 1])
        time = time[index]
        cur_event += 2

    # stores the event in the MNE format ([sample, 0, 0])
    good_samples = []

    # now we traverse the array of good times and accumulate blocks of length sample_size
    heap = []
    for t in time:
        # initial condition
        if len(heap) == 0:
            heap.append(t)
        # if not sequential, empty the heap and initialize it. Take twice sampling rate to avoid rounding errors
        elif (t - heap[-1]) > (2 * time_step):
            heap = [t]
        # otherwise, it's a sequence. Check if we're done to dump the entire heap
        else:
            heap.append(t)
            if len(heap) == sample_size:
                # convert from time point to sample
                sample = np.nonzero(original_time == heap[0])[0][0]
                good_samples.append([sample, 0, 0])
                heap = []

    events = np.array(good_samples)

    return events


def get_good_indexes(markers, time):
    ''' Returns a vector of indexes marking the time points with good data. Ideal for computation of covariance matrix. Receives markers (list with markers for artifacts), time (array with time vector).'''

    good_samples = np.arange(len(time))
    # first, we remove from the time vector all the bad segments
    cur_event = 0
    while cur_event < len(markers):
        index = (time < markers[cur_event]) | (time > markers[cur_event + 1])
        time = time[index]
        good_samples = good_samples[index]
        cur_event += 2

    return good_samples


def read_chl_events(raw, times, threshold=.5):
    ''' Returns a list of events with the time points where there was crossing of the head movement threshold (begin and end). raw is the raw structure, times is a time vector '''

    # just like the marker files, the goal here is to create events any time the CHL signal goes bad and then becomes good again (i.e. marking the bad segment)
    markers = []
    motion = hm.get_head_motion(raw)

    movement = np.sqrt(np.sum(motion**2, axis=0))

    # smooth the movement
    movement = mne.filter.low_pass_filter(movement, 300, 1)
    # store the sample locations where movement crosses threshold
    bad_segs = np.nonzero(movement >= threshold)[0]

    if len(bad_segs) > 0:
        # finding non-consecutive bad segments. We need to add one because we used diff() before
        start_bad_segs = np.nonzero(np.diff(bad_segs) > 1)[0] + np.ones(1)
        # add back the first bad segment
        start_bad_segs = np.concatenate(([0], start_bad_segs))
        # now start_bad_segs stores the positions when the bad segments started. Following the same logic, we compute the end of each segment
        end_bad_segs = np.nonzero(np.diff(bad_segs) > 1)[0]
        end_bad_segs = np.concatenate((end_bad_segs, [len(bad_segs) - 1]))
        start_end = np.sort(np.concatenate((start_bad_segs, end_bad_segs)))

        markers = [times[bad_segs[int(i)]] for i in start_end]

    return markers


def crop_clean_epochs(raw, events, seg_len=13):
    ''' Returns an Epochs structure with what epochs to use. raw is the usual structure, events is the MNE-like events array, and window_length is in seconds. '''

    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    epochs = mne.Epochs(raw, events, None, 0, seg_len, keep_comp=True, preload=True, baseline=(None, None), picks=picks)

    return epochs
