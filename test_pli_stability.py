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
plot_band = 0
data_len = np.hstack((np.r_[220:70:-20], 70))
subplot_inds = [2, 3, 4, 6, 7, 8, 10, 11, 12]

# first, the complete pli
pli, labels, bands = ve.compute_all_labels_pli('SFBPPSAH')
plis = [pli[plot_band]]

vmin = np.inf
vmax = -np.inf
for l in data_len:
    pli, labels, bands = ve.compute_all_labels_pli('SFBPPSAH', tmax=l)
    if vmax < np.amax(pli[plot_band]):
        vmax = np.amax(pli[plot_band])
    if vmin > np.amin(pli[plot_band]):
        vmin = np.amin(pli[plot_band])

    plis.append(pli[plot_band])


ax = pl.subplot(3, 4, 5)
plot_pli(plis[0], ax=ax, limits=[vmin, vmax], cbar=True)
ax.set_title(240)

for axid, l in enumerate(data_len):
    ax = pl.subplot(3, 4, subplot_inds[axid])
    plot_pli(plis[axid+1], ax=ax, limits=[vmin, vmax], cbar=False)
    ax.set_title(data_len[axid])

pl.show(block=False)
