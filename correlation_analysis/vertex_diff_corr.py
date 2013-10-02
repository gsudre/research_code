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


def construct_matrix(data, rois, roi_labels, hemi, idx):
# Reorganizes the vertices by ROI
    Y = np.empty([np.sum(idx), data.shape[1]])
    verts = []
    cnt = 0
    for r, roi in enumerate(rois):
        verts_in_roi = len(roi)
        if verts_in_roi > 0:
            Y[:,cnt:(cnt+verts_in_roi)] = data[idx,roi]
            cnt += verts_in_roi
            tmp_verts = [roi_labels[r] for i in range(verts_in_roi)]
            verts += tmp_verts
    return Y, verts


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
big = 10^5

base_corrs = []
last_corrs = []
delta_corrs = []
matched_gf = np.recfromcsv('/Users/sudregp/data/structural/gf_1473_matched_on18.csv')
for g in group:
    idx = np.logical_and(matched_gf['group3']==('"""%s"""'%g),matched_gf['match_outcome']==1)
    idx_base = np.zeros((len(idx)), dtype=bool)
    idx_last = np.zeros((len(idx)), dtype=bool)
    # find out all scans for each unique subject
    subjects = np.unique(matched_gf[idx]['personx'])  # only look at subjects that obeyed previous criteria
    cnt=0
    for subj in subjects:
        good_subj_scans = np.nonzero(np.logical_and(matched_gf['personx']==subj,idx))[0]
        # only use subjects with one scan < 18 and another after 18
        ages = matched_gf[good_subj_scans]['agescan']
        if len(ages) > 1 and np.min(ages)<18 and np.max(ages) > 18:
            print ages
            ages = np.argsort(ages)
            # makes the first scan true
            idx_base[good_subj_scans[ages[0]]] = True
            # makes the last scan true
            idx_last[good_subj_scans[ages[-1]]] = True
            cnt+=1

    num_subjects = np.sum(np.logical_and(idx,idx_base))
    # create huge array so we can add all the data and thenresize it appropriately
    raw_base = np.empty([num_subjects, big])
    raw_last = np.empty([num_subjects, big])
    # verts will be a list of strings, with the name of the ROI the vertex belongs to
    verts = []
    for b in brain:
        print 'Working on ' + b
        for h in hemi:

            data_roi_labels, data_roi_verts = load_rois('%s/data/structural/labels/%s_%s_labels.txt'%(os.path.expanduser('~'), b, h), b)
            data = load_structural('%s/data/structural/baseline_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_lt18.csv' % (os.path.expanduser('~'), b, h, g))
            X, vert_labels = construct_matrix(data, data_roi_verts, data_roi_labels, h, np.logical_and(idx,idx_base))
            raw_base = np.hstack((raw_base, X))
            # verts are the same for both baseline and last scan
            verts = np.hstack((verts, vert_labels))

            ## now we add in the same subjects' last scan
            #data = load_structural('%s/data/structural/last_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_mt18.csv' % (os.path.expanduser('~'), b, h, g))
            #X, vert_labels = construct_matrix(data, data_roi_verts, idx)
            #raw_last = np.hstack((raw_last, X))

    # when we're done gathering all the data, compute the correlations
    print 'Computing correlations\n'
    num_vertices = raw_base.shape[1]
    corr_base = np.empty((num_vertices,num_vertices))
    corr_last = np.empty((num_vertices,num_vertices))
    corr_base[:] = np.NAN
    corr_last[:] = np.NAN
    for x in range(num_vertices):
        print 'vertex', x+1, '/', num_vertices
        for y in range(x+1,num_vertices):
            corr_base[x, y] = scipy.stats.pearsonr(raw_base[:, x], raw_base[:, y])
            corr_last[x, y] = scipy.stats.pearsonr(raw_last[:, x], raw_last[:, y])
    base_corrs.append(corr_base)
    last_corrs.append(corr_last)
    delta_corrs.append(corr_last-corr_base)
