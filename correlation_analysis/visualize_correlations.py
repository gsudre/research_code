import numpy as np
import os
import scipy
import pylab as pl
import pdb
from scipy import stats


def load_structural(fname):
    data = np.genfromtxt(fname, delimiter=',')
    # removing first column and first row, because they're headers
    data = scipy.delete(data, 0, 1)
    data = scipy.delete(data, 0, 0)
    # format it to be subjects x variables
    data = data.T
    return data


def load_rois(fname, brain):
    roi_vertices = []
    roi_labels = []
    labels = np.genfromtxt(fname)
    if brain=='thalamus':
        rois = thalamus_labels
    elif brain=='striatum':
        rois = striatum_labels
    elif brain=='gp':
        rois = gp_labels
    elif brain=='cortex':
        rois = cortex_labels
    else:
        rois = []
    for r in rois:
        roi_labels.append(r[0])
        vert_list = [np.nonzero(labels == i)[0] for i in r[1]]
        # merge all vertices into one big array
        verts = []
        for v in vert_list:
           verts = np.concatenate((verts, v))
        roi_vertices.append(verts.astype(np.int32))
    return roi_labels, roi_vertices


def construct_matrix(data, rois, brain):
    num_subjects = data.shape[0]
    Y = np.zeros([num_subjects, len(rois)])
    for r, roi in enumerate(rois):
        if len(roi)==0:
            Y[:, r] = 0
        else:
            Y[:, r] = stats.nanmean(data[:, roi], axis=1)
    return Y


def get_corr(X, Y):
    corr = np.empty([X.shape[1], Y.shape[1]])
    pval = np.empty([X.shape[1], Y.shape[1]])
    for x in range(X.shape[1]):
        for y in range(Y.shape[1]):
            corr[x, y], pval[x, y] = stats.pearsonr(X[:, x], Y[:, y])
    return corr

# this summarizes what ROIs will be plotted in each plot, in this order.
# Try to organize it from posterior to anterior!
thalamus_labels = [['Pulvinar', [8]], ['Lateral Posterior', [6]],
                    ['Lateral Dorsal', [5]], ['VP', [11]], ['VL', [10]],
                    ['VA', [9]], ['Anterior nuclei', [3]], ['Medial Dorsal', [7]],
                    ['Central nuclei', [4]]]
striatum_labels = [['Tail Caudate', [104.176]], ['Head Caudate', [102.118]],
                    ['Nucleus Accumbens', [100.059]], ['Post Putamen', [105]],
                    ['Ant Putamen', [100.882]]]
gp_labels = [['Posterior', [12]], ['Inferior_anterior', [11.0118]], ['Superior_anterior', [4.98824]]]
cortex_labels = [['Occipital', [132, 38, 63, 97, 175, 112, 251, 98, 154, 37, 54, 69]],
                ['Parietal', [88, 60, 41, 32, 110, 52, 41, 159, 56, 74]],
                ['Temporal', [145, 130, 140, 26, 165, 99, 139, 125, 61, 64, 164, 62, 119, 196, 118, 18]],
                ['PostCentral', [74, 110]], ['Precentral', [5, 80]],
                ['Frontal', [10, 2, 75, 5, 6, 1, 7, 70, 50, 15, 80, 90, 85, 27]],
                ['Cingulate', [7, 27]]]

group = 'remission'
brain = ['cortex', 'striatum']
hemi = ['L', 'R']

for h in hemi:
    data1_roi_labels, data1_roi_verts = load_rois('%s/data/structural/labels/%s_%s_labels.txt'%(os.path.expanduser('~'), brain[0], h), brain[0])
    data2_roi_labels, data2_roi_verts = load_rois('%s/data/structural/labels/%s_%s_labels.txt'%(os.path.expanduser('~'), brain[1], h), brain[1])
    data1 = load_structural('%s/data/structural/baseline_%s%s_SA_%s_lt18.csv' % (os.path.expanduser('~'), brain[0], h, group))
    data2 = load_structural('%s/data/structural/baseline_%s%s_SA_%s_lt18.csv' % (os.path.expanduser('~'), brain[1], h, group))
    X = construct_matrix(data1, data1_roi_verts, brain[0])
    Y = construct_matrix(data2, data2_roi_verts, brain[1])
    corr_base = get_corr(X, Y)

    data1 = load_structural('%s/data/structural/last_%s%s_SA_%s_mt18.csv' % (os.path.expanduser('~'), brain[0], h, group))
    data2 = load_structural('%s/data/structural/last_%s%s_SA_%s_mt18.csv' % (os.path.expanduser('~'), brain[1], h, group))
    X = construct_matrix(data1, data1_roi_verts, brain[0])
    Y = construct_matrix(data2, data2_roi_verts, brain[1])
    corr_last = get_corr(X, Y)

    diff_corr = corr_last - corr_base

    pl.figure()
    pl.subplot(1,3,1)
    ax1 = pl.imshow(corr_base, interpolation='none');
    pl.colorbar(shrink=.5)
    pl.title('Baseline (%s), %s, n=%d' % (h, group, X.shape[0]))
    # first picture gets X and Y labels
    pl.xticks(range(corr_base.shape[1]), data2_roi_labels ,rotation='vertical')
    pl.yticks(range(corr_base.shape[0]), data1_roi_labels)
    pl.subplot(1,3,2)
    ax2 = pl.imshow(corr_last, interpolation='none');
    pl.colorbar(shrink=.5)
    pl.title('Last (%s), %s, n=%d' % (h, group, X.shape[0]))
    # matching colorbars
    base_min, base_max = ax1.get_clim()
    last_min, last_max = ax2.get_clim()
    if base_min < last_min:
        the_min = base_min
    else:
        the_min = last_min
    if base_max > last_max:
        the_max = base_max
    else:
        the_max = last_max
    ax1.set_clim(the_min, the_max)
    ax2.set_clim(the_min, the_max)
    pl.subplot(1,3,3)
    ax3 = pl.imshow(diff_corr, interpolation='none');
    pl.colorbar(shrink=.5);
    pl.title('Last - Baseline (%s)' % group)
    pl.show(block=False)
