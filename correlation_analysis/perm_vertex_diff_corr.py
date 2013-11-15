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

groups = ['NV', 'persistent']
num_perms = 100
brain = ['striatum', 'thalamus']
hemi = ['R']
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
                data = load_structural('%s/data/structural/%s_%s%s_%s_SA_QCCIVETlt35_QCSUBePASS_MATCHDIFF_on18_dsm5_2to1.csv' % (os.path.expanduser('~'), t, b, h, group))
                group_subjects = data.shape[0]
                nverts = data.shape[1]
                raw[num_subjects:(num_subjects+group_subjects),cnt:(cnt+nverts)] = data
                cnt += nverts
        num_subjects += group_subjects
        subjects_per_group[group] = group_subjects
    # trimming the matric to the correct number of vertices and subjects
    print 'Resizing matrices'
    num_vertices = cnt
    raw_data.append(raw[:num_subjects, :num_vertices])

diff_base = []
diff_last = []
diff_delta = []
subj_split = subjects_per_group[groups[0]]
idx1 = np.array(range(6178))
idx2 = 6178 + np.array(range(3108))
for p in range(num_perms):
    print 'Perm', p+1, '/', num_perms
    subj_labels = np.random.permutation(num_subjects)

    cor1b = np.float16(np.corrcoef(raw_data[0][subj_labels[:subj_split], :], rowvar=0))
    cor2b = np.float16(np.corrcoef(raw_data[0][subj_labels[subj_split:], :], rowvar=0))
    data1 = [list(cor1b[i, idx2]) for i in idx1]
    data1 = [j for k in data1 for j in k]
    data2 = [list(cor2b[i, idx2]) for i in idx1]
    data2 = [j for k in data2 for j in k]
    diff_base.append(1 - stats.spearmanr(data1, data2)[0])

    cor1l = np.float16(np.corrcoef(raw_data[1][subj_labels[:subj_split], :], rowvar=0))
    cor2l = np.float16(np.corrcoef(raw_data[1][subj_labels[subj_split:], :], rowvar=0))
    data1 = [list(cor1l[i, idx2]) for i in idx1]
    data1 = [j for k in data1 for j in k]
    data2 = [list(cor2l[i, idx2]) for i in idx1]
    data2 = [j for k in data2 for j in k]
    diff_last.append(1 - stats.spearmanr(data1, data2)[0])

    delta1 = cor1l - cor1b
    delta2 = cor2l - cor2b
    data1 = [list(delta1[i, idx2]) for i in idx1]
    data1 = [j for k in data1 for j in k]
    data2 = [list(delta2[i, idx2]) for i in idx1]
    data2 = [j for k in data2 for j in k]
    diff_delta.append(1 - stats.spearmanr(data1, data2)[0])

np.savez('%s/data/results/structural/perms/perm_verts_striatumRthalamusR_corr_%sVS%s_%04d'%(
        os.path.expanduser('~'), groups[0], groups[1], np.random.randint(0, 9999)),
        diff_base=diff_base, diff_last=diff_last, diff_delta=diff_delta)
