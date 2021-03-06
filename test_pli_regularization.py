import pylab as pl
import numpy as np
import virtual_electrode as ve


def plot_pli(A, ax=None, limits=None, cbar=True):

    # makes A a mirror matrix (mirrowing the lower triangle)
    n = A.shape[0]
    A[np.triu_indices(n)] = A.T[np.triu_indices(n)]

    if not ax:
        fig = pl.figure()
        ax = fig.add_subplot(111)
    else:
        fig = pl.gcf()

    if limits:
        mappable = ax.imshow(A, interpolation="nearest", vmin=limits[0], vmax=limits[1])
    else:
        mappable = ax.imshow(A, interpolation="nearest")

    ax.grid(False)
    ax.get_xaxis().set_visible(False)
    ax.get_yaxis().set_visible(False)
    if cbar:
        cbar = fig.colorbar(mappable, ax=ax)


# def plot_many_pli():
data_len = [.0001, .001, .01, .1, 1, 10, 100, 1000, 10000]
band_names = ['delta', 'theta', 'alpha', 'beta', 'gamma']
subplot_inds = [2, 3, 4, 6, 7, 8, 10, 11, 12]
subj = 'CVKRVURL'

# first, the complete pli
pli, labels, bands = ve.compute_all_labels_pli(subj)
plis = [pli]

# then compute it for the chopped data
for l in data_len:
    pli, labels, bands = ve.compute_all_labels_pli(subj, reg=l)
    plis.append(pli)

# now that we're done with the heavy computation, let's plot every band
for plot_band, band_name in enumerate(band_names):

    fig = pl.figure()

    # figure out the color axis
    vmin = np.inf
    vmax = -np.inf
    for l in range(len(data_len)):
        if vmax < np.amax(plis[l][plot_band]):
            vmax = np.amax(plis[l][plot_band])
        if vmin > np.amin(plis[l][plot_band]):
            vmin = np.amin(plis[l][plot_band])

    ax = pl.subplot(3, 4, 5)
    plot_pli(plis[0][plot_band], ax=ax, limits=[vmin, vmax], cbar=True)
    ax.set_title(band_name + '_pen' + str(0))

    for axid, l in enumerate(data_len):
        ax = pl.subplot(3, 4, subplot_inds[axid])
        plot_pli(plis[axid+1][plot_band], ax=ax, limits=[vmin, vmax], cbar=False)
        ax.set_title(data_len[axid])

    pl.savefig(subj + '_' + band_name + 'reg.png')
    pl.show(block=False)
