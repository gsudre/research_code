import numpy as np
import os
import scipy
import matplotlib.mlab as mlab
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
            Y[:, r] = np.nansum(data[:, roi], axis=1)
    return Y


# this summarizes what ROIs will be plotted in each plot, in this order.
# Try to organize it from posterior to anterior!
thalamus_labels = [['Pulvinar', [8]], ['Lateral Posterior', [6]],
                    ['Lateral Dorsal', [5]], ['VP', [11]], ['VL', [10]],
                    ['VA', [9]], ['Anterior nuclei', [3]], ['Medial Dorsal', [7]],
                    ['Central nuclei', [4]]]
striatum_labels = [['Tail Caudate', [104.176]], ['Head Caudate', [102.118]],
                    ['Nucleus Accumbens', [100.059]], ['Post Putamen', [105]],
                    ['Ant Putamen', [100.882]]]
gp_labels = [['Posterior', [12]], ['Anterior', [11.0118, 4.98824]]]
cortex_labels = [['Occipital', [132, 38, 63, 97, 175, 112, 251, 98, 154, 37, 54, 69]],
                ['Parietal', [88, 60, 41, 32, 110, 52, 41, 159, 56, 74]],
                ['Temporal', [145, 130, 140, 26, 165, 99, 139, 125, 61, 64, 164, 62, 119, 196, 118, 18]],
                ['PostCentral', [74, 110]], ['Precentral', [5, 80]],
                ['Frontal', [10, 2, 75, 5, 6, 1, 7, 70, 50, 15, 80, 90, 85, 27]],
                ['Cingulate', [7, 27]]]

group = ['NV', 'persistent', 'remission']
brain = ['striatum', 'gp', 'cortex', 'thalamus']
hemi = ['L', 'R']

var_names = []
for b in brain:
    print 'Working on ' + b
    for h in hemi:
        data_roi_labels, data_roi_verts = load_rois('%s/data/structural/labels/%s_%s_labels.txt'%(os.path.expanduser('~'), b, h), b)
        dtype = [('subject', object), ('visit', object), ('group', object)] + [(roi, float) for roi in data_roi_labels]
        array = np.recarray(0, dtype=dtype)
        num_subjs = 0 # index to make different subject names per group
        for g in group:

            data = load_structural('%s/data/structural/baseline_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_lt18_dsm5.csv' % (os.path.expanduser('~'), b, h, g))
            X = construct_matrix(data, data_roi_verts, b)

            N = X.shape[0]
            subj_names = ['subj' + str(i+1+num_subjs) for i in range(N)]

            base = np.recarray(N, dtype=dtype)
            for r in range(N):
                base[r] = (subj_names[r], 'baseline', g) + tuple(X[r, :])
            array = np.concatenate((array, base), axis=0)

            # now we add in the same subjects' last scan
            data = load_structural('%s/data/structural/last_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_mt18_dsm5.csv' % (os.path.expanduser('~'), b, h, g))
            X = construct_matrix(data, data_roi_verts, b)
            last = np.recarray(N, dtype=dtype)
            for r in range(N):
                last[r] = (subj_names[r], 'last', g) + tuple(X[r, :])
            array = np.concatenate((array, last), axis=0)

            num_subjs += N
        mlab.rec2csv(array, '/Users/sudregp/data/structural/roisSum_%s%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_dsm5.csv'%(b,h))
