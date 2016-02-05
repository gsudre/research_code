# Plots and saves the vertex-based subcortical correlation
import numpy as np
import os
import pylab as pl

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

execfile('/Users/sudregp/research_code/save_to_brainview.py')

# Note that we need to plot differences because if we just plot one group most
# vertices inside the same ROI will be highly correlated!
# g1 = 'remission'
g2 = 'NV'
# make sure this is in the same order as in vertex_diff_corr.py
brain = ['gp', 'thalamus']
hemi = ['R']
# res1 = np.load('%s/data/results/structural/verts_corr_matchdiff_dsm4_%s.npz'%(os.path.expanduser('~'), g1))
res2 = np.load('/Users/sudregp/data/results/structural/TMPverts_corr.npz') #'%s/data/results/structural/verts_corr_matchdiff_dsm4_%s.npz'%(os.path.expanduser('~'), g2))
# mat = (res1['allcorrs'][1] - res1['allcorrs'][0]) - (res2['allcorrs'][1] - res2['allcorrs'][0])
mat = res2['mycorr']

# collapse the vertices so that we have one connectivity value per vertex
# conn = np.mean(mat, axis=0)

# now we need to re-order each vertex so that they're in their correct position
start = 0
cnt = 0
for b in brain:
    print 'Working on', b
    for h in hemi:
        data_roi_labels, data_roi_verts = load_rois('%s/data/structural/labels/%s_%s_labels.txt'%(os.path.expanduser('~'), b, h), b)
        # first, figure out how many vertices are in this brain region
        nverts = np.max([np.max(v) for v in data_roi_verts])+1
        # figure out what indexes of the correlation matrix belong to this brain region
        idx = cnt + np.array(range(nverts))
        cnt += nverts
        # get everything not in this brain region
        not_here = np.setdiff1d(range(mat.shape[1]), idx)
        # create a matrix to store the correct values
        my_conn = np.zeros(nverts)
        for v in data_roi_verts:
            my_conn[v] = np.mean(mat[start:(start+len(v)), not_here], axis=1)
            # shift the pointer so we start in the right place next time
            start += len(v)
        fname = ('%s/data/results/structural/TMP.txt' %
                (os.path.expanduser('~')))
        write_bv(my_conn, fname)
