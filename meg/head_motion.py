#! /usr/bin/python

import numpy as np
import mne


def get_head_motion(raw, plot=False):
    fiducials = ['NASION', 'LPA', 'RPA']
    chans = {fiducials[0]: ['HLC0011', 'HLC0012', 'HLC0013'], fiducials[1]: ['HLC0021', 'HLC0022', 'HLC0023'], fiducials[2]: ['HLC0031', 'HLC0032', 'HLC0033']}

    m = raw.info['dev_head_t']
    if m is None:
        print '\tCould not find device->head transform in FIF file!'
        return None
    else:
        m = m['trans']    # 4x4 transform
    r = m[0:3, 0:3]         # 3x3 rotation
    t = m[0:3, 3]           # translation

    fid_data = np.zeros([len(fiducials), raw.n_times])
    for f, fid in enumerate(fiducials):
        mask = chans[fid][0][:-1]  # gets everything but the last channel name char
        picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], mask + '.')
        if len(picks) < 3:
            print 'File does not have CHL!'
            return None
        else:
            start, stop = raw.time_as_index([0, 240])  # read the first 15s of data
            data, times = raw[picks[:3], :]#start:(stop + 1)]
            data = data.T * 100  # m -> cm
            o = np.inner(data[0, :], r) + t  # set the origin to the first data point
            data = np.inner(data, r) + t - o  # rotate and translate
            # combine X, Y, Z
            fid_data[f, :] = np.sqrt(np.sum(data.T**2, axis=0))

    if plot:
        import pylab as pl
        for i in [0, 1, 2]:
            pl.plot(times, fid_data[i, :])
            pl.hold(1)
        pl.title("RMS movement for each fiducial marker")
        pl.xlabel("seconds")
        pl.ylabel("cm")
        pl.show(block=False)

    return fid_data

# Returns the maximum head motion (sqrt(x2+y2+z2)) 
def get_max_motion(raw, smin=0, smax=None):
    motion_data = get_head_motion(raw)
    if motion_data is None:
        return np.Inf
    else:
        if smax is None:
            smax = motion_data.shape[-1]
        movement = np.sqrt(np.sum(motion_data[:, smin:smax]**2, axis=0))
        return np.amax(movement)

# Returns the difference in head motion between end eng start of recording 
def get_delta_motion(raw):
    motion_data = get_head_motion(raw)
    if motion_data is None:
        return np.Inf
    else:
        movement = np.sqrt(np.sum(motion_data**2, axis=0))
        return movement[-1]-movement[0]

# Returns the maximum head displacement across axes, and the axes in which it occurred 
def get_max_axis(raw, smin=0, smax=None):
    motion_data = get_head_motion(raw)
    if motion_data is None:
        return None
    else:
        if smax is None:
            smax = motion_data.shape[-1]
        movement = np.amax(motion_data[:, smin:smax], axis=1)
        max_axis = np.argmax(movement)
        if max_axis==0:
            return [movement[0], 'X']
        elif max_axis==1:
            return [movement[1], 'Y']
        else:
            return [movement[2], 'Z']

# Returns the difference in between end and start positions across axes, and the axes in which it occurred 
def get_delta_axis(raw):
    motion_data = get_head_motion(raw)
    if motion_data is None:
        return None
    else:
        delta = motion_data[:, -1] - motion_data[:, 0]
        max_axis = np.argmax(delta)
        if max_axis==0:
            return [delta[max_axis], 'X']
        elif max_axis==1:
            return [delta[max_axis], 'Y']
        else:
            return [delta[max_axis], 'Z']
