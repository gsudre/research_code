#! /usr/bin/python

import numpy as np
import mne


def get_head_motion(raw, plot=False):
    fiducials = ['NASION', 'LPA', 'RPA']
    chans = {fiducials[0]: ['HLC0011', 'HLC0012', 'HLC0013'], fiducials[1]: ['HLC0021', 'HLC0022', 'HLC0023'], fiducials[2]: ['HLC0031', 'HLC0032', 'HLC0033']}

    m = raw.info['dev_head_t']['trans']    # 4x4 transform
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
            data, times = raw[picks[:3], start:(stop + 1)]
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
