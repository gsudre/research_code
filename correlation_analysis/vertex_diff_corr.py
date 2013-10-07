import numpy as np
import os
import scipy
import matplotlib.mlab as mlab
import pdb
from scipy import stats
import pdb as pb


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


def construct_matrix(data, rois, roi_labels, hemi):
# Reorganizes the vertices by ROI
    Y = np.empty([data.shape[0], init_verts],dtype=np.float16)
    Y[:] = np.nan
    verts = []
    cnt = 0
    for r, roi in enumerate(rois):
        verts_in_roi = len(roi)
        if verts_in_roi > 0:
            Y[:,cnt:(cnt+verts_in_roi)] = data[:,roi]
            cnt += verts_in_roi
            tmp_verts = [hemi + '_' + roi_labels[r] for i in range(verts_in_roi)]
            verts += tmp_verts
    Y = Y[:Y.shape[0], :len(verts)]
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

group = 'NV' #, 'persistent', 'remission'
brain = ['striatum', 'gp', 'thalamus']
hemi = ['L', 'R']
time = ['baseline', 'last']
init_verts = 10e5
init_subjs = 100

all_corrs = []
matched_gf = np.recfromcsv('/Users/sudregp/data/structural/gf_1473_dsm45_matched_on18_dsm4.csv')
for t in time:
    # create huge array so we can add all the data and thenresize it appropriately
    raw = np.empty([init_subjs, init_verts],dtype=np.float16)
    raw[:] = np.nan
    # verts will be a list of strings, with the name of the ROI the vertex belongs to
    verts = []
    cnt = 0
    for b in brain:
        print 'Working on ' + b
        for h in hemi:
            data_roi_labels, data_roi_verts = load_rois('%s/data/structural/labels/%s_%s_labels.txt'%(os.path.expanduser('~'), b, h), b)
            if t == 'baseline':
                data = load_structural('%s/data/structural/%s_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_lt18.csv' % (os.path.expanduser('~'), t, b, h, group))
            else:
                data = load_structural('%s/data/structural/%s_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_mt18.csv' % (os.path.expanduser('~'), t, b, h, group))
            num_subjects = data.shape[0]
            X, vert_labels = construct_matrix(data, data_roi_verts, data_roi_labels, h)
            raw[0:num_subjects,cnt:(cnt+len(vert_labels))] = X
            cnt += len(vert_labels)
            # verts are the same for both baseline and last scan
            verts = verts + vert_labels
    # trimming the matric to the correct number of vertices and subjects
    print 'Resizing matrices'
    num_vertices = len(verts)
    raw = raw[:num_subjects, :num_vertices]

    # when we exclude the cortex, we can compute all at once
    all_corrs.append(np.float16(np.corrcoef(raw,rowvar=0)))
#    # when we're done gathering all the data, compute the correlations
#    print 'Computing correlations\n'
#    num_vertices = raw.shape[1]
#    corrs = []
#    for x in range(num_vertices):
#        print 'vertex', x, '/', num_vertices
#        for y in range(x, num_vertices):
#            corrs.append(np.float16(scipy.stats.pearsonr(raw[:, x], raw[:, y])[0]))
#    all_corrs.append(corrs)
np.savez('%s/data/results/structural/verts_corr_%s'%(os.path.expanduser('~'), group),
        allcorrs=all_corrs, verts=verts)
