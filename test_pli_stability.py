'''

Set of function to test the stability of PLI estimates after varying the amount of data that goes in for calculating the covariance matrix.

'''

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


def plot_many_pli(subj, plis, data_len, reg):

    band_names = ['delta', 'theta', 'alpha', 'beta', 'gamma']
    subplot_inds = [2, 3, 4, 6, 7, 8, 10, 11, 12]
    # now that we're done with the heavy computation, let's plot every band
    for plot_band, band_name in enumerate(band_names):

        pl.figure()

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
        ax.set_title(band_name + '_' + str(240))

        for axid, l in enumerate(data_len):
            ax = pl.subplot(3, 4, subplot_inds[axid])
            plot_pli(plis[axid+1][plot_band], ax=ax, limits=[vmin, vmax], cbar=False)
            ax.set_title(data_len[axid])

        pl.savefig(subj + '_' + band_name + 'reg' + str(reg) + '.png')
        pl.show(block=False)


def compute_stability(subj, fix_vertex=True, reg=0):

    data_len = np.hstack((np.r_[220:70:-20], 70))
    # first, the complete pli
    pli, labels, bands, selected_voxels = ve.compute_all_labels_pli(subj, reg=reg)
    plis = [pli]

    # then compute it for the chopped data
    if not fix_vertex:
        selected_voxels = None

    for l in data_len:
        pli, labels, bands, junk = ve.compute_all_labels_pli(subj, tmax=l, reg=reg, selected_voxels=selected_voxels)
        plis.append(pli)

    return plis, labels
