"""

Plots the PSD for NV and ADHD to sanity check the data based on the results
of the Wilson, 2011 paper.

"""
# Authors: Gustavo Sudre, 01/2013

import numpy as np
from mne import fiff

filename = '/Users/sudregp/MEG_data/analysis/rest/good_PSDS.npz'
limits = [[1, 4], [4, 7], [8, 14], [14, 30], [30, 56], [64, 82], [82, 106], [124, 150]]

npzfile = np.load(filename)
psds = npzfile['psds']
adhd = npzfile['adhd']
freqs = npzfile['freqs']


def plot_bars(psds, adhd, freqs, aux_title=None):
# psds is subjects x channels x freqs

    import matplotlib.pyplot as plt

    fig = plt.figure()
    ax = fig.add_subplot(111)

    ## the data
    N = len(limits)

    ## necessary variables
    ind = np.arange(N)                # the x locations for the groups
    width = 0.35                      # the width of the bars

    adhd_rects = np.zeros(N)
    nv_rects = np.zeros(N)
    adhd_std = np.zeros(N)
    nv_std = np.zeros(N)
    xTickMarks = []
    for idx, bar in enumerate(limits):
        index = np.logical_and(freqs >= bar[0], freqs <= bar[1])
        band_psd = np.mean(psds[:, :, index], axis=2)
        channel_band_psd = np.mean(band_psd, axis=1)
        adhd_rects[idx] = np.mean(channel_band_psd[adhd])
        nv_rects[idx] = np.mean(channel_band_psd[~adhd])
        adhd_std[idx] = np.std(channel_band_psd[adhd]) / np.sum(adhd)
        nv_std[idx] = np.std(channel_band_psd[~adhd]) / np.sum(~adhd)
        xTickMarks.append(str(bar[0]) + ' - ' + str(bar[1]) + ' Hz')

    ## the bars
    rects1 = ax.bar(ind, adhd_rects, width, color='black', yerr=adhd_std, error_kw=dict(elinewidth=2, ecolor='red'))

    rects2 = ax.bar(ind + width, nv_rects, width, color='red', yerr=nv_std, error_kw=dict(elinewidth=2, ecolor='black'))

    # axes and labels
    ax.set_xlim(-width, len(ind) + width)
    # ax.set_ylim(0, 45)
    ax.set_ylabel('Power')
    ax.set_title('Power by band and group' + aux_title)
    # xTickMarks = ['Group' + str(i) for i in range(1, N + 1)]
    ax.set_xticks(ind + width)
    xtickNames = ax.set_xticklabels(xTickMarks)
    plt.setp(xtickNames, rotation=20, fontsize=10)

    ## add a legend
    ax.legend((rects1[0], rects2[0]), ('ADHD', 'NV'))

    plt.show()

# plotting all channels
plot_bars(psds, adhd, freqs, ': all sensors')

# plotting only the ones in the paper
ch_names = npzfile['info'][()]['ch_names']
picks = npzfile['picks'][()]
psd_channels = []
p = picks[::-1]
for i in p:
    psd_channels.append(ch_names.pop(i))
# now, select only the ones we want
look_for = ['M.F', 'M.T']
for sel in look_for:
    picks = fiff.pick_channels_regexp(psd_channels, sel)
    plot_bars(psds[:, picks, :], adhd, freqs, sel)
