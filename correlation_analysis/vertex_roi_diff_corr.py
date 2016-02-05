# Calculates the correlation between a given roi and vertices in different brian structures.
# Sets the correlation to the voxels within the ROI to 0.
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

roi = 'Nucleus Accumbens'
roi_hemi = 'R'
roi_brain = 'striatum'
groups = ['NV', 'persistent', 'remission']
brain = ['striatum', 'gp', 'thalamus']
hemi = ['L', 'R']
time = ['baseline', 'last']
init_verts = 10e5
init_subjs = 100

# start by grabbing the ROI data
data_roi_labels, data_roi_verts = load_rois('%s/data/structural/labels/%s_%s_labels.txt' %
                                            (os.path.expanduser('~'), roi_brain, roi_hemi), roi_brain)
for group in groups:
    print '===', group, '==='
    for b in brain:
        print 'Working on ' + b
        for h in hemi:
            all_corrs = []
            for t in time:
                if t == 'baseline':
                    roi_data = load_structural('%s/data/structural/%s_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_lt18.csv' %
                                (os.path.expanduser('~'), t, roi_brain, roi_hemi, group))
                    data = load_structural('%s/data/structural/%s_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_lt18.csv' % (os.path.expanduser('~'), t, b, h, group))
                else:
                    roi_data = load_structural('%s/data/structural/%s_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_mt18.csv' %
                                (os.path.expanduser('~'), t, roi_brain, roi_hemi, group))
                    data = load_structural('%s/data/structural/%s_%s%s_SA_%s_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_mt18.csv' %
                                            (os.path.expanduser('~'), t, b, h, group))
                # group the roi SA values
                roi_sa = np.nansum(roi_data[:, data_roi_verts[data_roi_labels.index(roi)]], axis=1)

                # compute the correlation between the summed value and all the other voxels
                num_vertices = data.shape[1]
                corr = np.empty(num_vertices)
                for v in range(num_vertices):
                    corr[v] = np.corrcoef(data[:,v], roi_sa)[0,1]
                # set the voxels within the ROI to 0 correlation if necessary
                if (roi_brain==b) and (roi_hemi==h):
                    corr[data_roi_verts[data_roi_labels.index(roi)]] = 0

                all_corrs.append(np.float16(corr))
            # save the file for brain-view2
            corrs = all_corrs[1] - all_corrs[0]
            fname = ('%s/data/results/structural/vertDeltaCorr_%s_%s%s_roi%s%s.txt' %
                    (os.path.expanduser('~'), group, h, b, roi_hemi, roi.replace(' ','_')))
            fid = open(fname,'w')
            fid.write('<header>\n</header>\nDeltaFU_Baseline\n')
            for v in corrs:
                fid.write('%.4f\n'%v)
            fid.close()
