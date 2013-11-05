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

groups = ['NV', 'persistent']
num_perms = 10
brain = ['striatum', 'gp', 'thalamus']
hemi = ['L', 'R']
time = ['base', 'last']
init_verts = 10e5
init_subjs = 100
subjects_per_group = {}

raw_data = []
for t in time:
    # create huge array so we can add all the data and thenresize it appropriately
    raw = np.empty([init_subjs, init_verts],dtype=np.float16)
    raw[:] = np.nan
    num_subjects = 0
    for group in groups:
        cnt = 0
        for b in brain:
            print 'Working on ' + b + ' for ' + group
            for h in hemi:
                data_roi_labels, data_roi_verts = load_rois('%s/data/structural/labels/%s_%s_labels.txt'%(os.path.expanduser('~'), b, h), b)
                data = load_structural('%s/data/structural/%s_%s%s_%s_SA_QCCIVETlt35_QCSUBePASS_MATCHDIFF_on18_dsm5_2to1.csv' % (os.path.expanduser('~'), t, b, h, group))
                group_subjects = data.shape[0]
                X, vert_labels = construct_matrix(data, data_roi_verts, data_roi_labels, h)
                raw[num_subjects:(num_subjects+group_subjects),cnt:(cnt+len(vert_labels))] = X
                cnt += len(vert_labels)
        num_subjects += group_subjects
        subjects_per_group[group] = group_subjects
    # trimming the matric to the correct number of vertices and subjects
    print 'Resizing matrices'
    num_vertices = cnt
    raw_data.append(raw[:num_subjects, :num_vertices])

diff_base = []
diff_last = []
diff_delta = []
diff_base_ed = []
diff_last_ed = []
diff_delta_ed = []
subj_split = subjects_per_group[groups[0]]
iu = np.triu_indices(raw_data[0].shape[1], k=1)
for p in range(num_perms):
    print 'Perm', p+1, '/', num_perms
    subj_labels = np.random.permutation(num_subjects)
    cor1b = np.float16(np.corrcoef(raw_data[0][subj_labels[:subj_split], :], rowvar=0))
    cor2b = np.float16(np.corrcoef(raw_data[0][subj_labels[subj_split:], :], rowvar=0))
    diff_base.append(1 - stats.spearmanr(cor1b[iu], cor2b[iu])[0])
    diff_base_ed.append(np.linalg.norm(cor1b[iu]-cor2b[iu]))

    cor1l = np.float16(np.corrcoef(raw_data[1][subj_labels[:subj_split], :], rowvar=0))
    cor2l = np.float16(np.corrcoef(raw_data[1][subj_labels[subj_split:], :], rowvar=0))
    diff_last.append(1 - stats.spearmanr(cor1l[iu], cor2l[iu])[0])
    diff_last_ed.append(np.linalg.norm(cor1l[iu]-cor2l[iu]))

    delta1 = cor1l - cor1b
    delta2 = cor2l - cor2b
    diff_delta.append(1 - stats.spearmanr(delta1[iu], delta2[iu])[0])
    diff_delta_ed.append(np.linalg.norm(delta1[iu]-delta2[iu]))

np.savez('%s/data/results/structural/perms/perm_verts_corr_%sVS%s_%04d'%(
        os.path.expanduser('~'), groups[0], groups[1], np.random.randint(0, 9999)),
        diff_base=diff_base, diff_last=diff_last, diff_delta=diff_delta,
        diff_base_ed=diff_base_ed, diff_last_ed=diff_last_ed, diff_delta_ed=diff_delta_ed)
