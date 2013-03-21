# Function to find segment of good data in resting study
# by Gustavo Sudre, March 2013
import mne
import numpy as np
import env


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


def find_good_epochs(raw, window_length=13, step_length=1, threshold=4000e-13, verbose=1):
    ''' Returns an Epochs structure with what time periods to use. window_length and step_length are in seconds'''

    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    data, time = raw[picks, :]

    ''' We search for windows of the given length. If a good window is found, add it to the list and check the next window (non-overlapping). If the current window is no good, step to the next available window. '''

    events = []
    cur = 0
    window_size = int(window_length * raw.info['sfreq'])
    step_size = int(step_length * raw.info['sfreq'])
    while cur + window_size < len(time):
        chunk = data[:, cur:(cur + window_size)]
        peak2peak = abs(np.amax(chunk, axis=1) - np.amin(chunk, axis=1))
        num_good_channels = np.sum(peak2peak < threshold, axis=0)
        if num_good_channels == len(picks):
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
