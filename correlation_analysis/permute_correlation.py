import numpy as np
import os
import scipy
from scipy import stats
import pylab as pl


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


def get_correlations(X, Y):
    corr = np.empty([X.shape[1], Y.shape[1]])
    pval = np.empty([X.shape[1], Y.shape[1]])
    for x in range(X.shape[1]):
        for y in range(Y.shape[1]):
            corr[x, y], pval[x, y] = stats.pearsonr(X[:, x], Y[:, y])
    return corr

# re-run the ROI analysis but first permute the subjects in their groups
groups = ['persistent', 'NV']
brain = ['thalamus', 'gp']
hemi = 'L'
num_perms = 2000

# load the data for both groups, both structures
Xs = []
Ys = []
data1_roi_labels, data1_roi_verts = load_rois('%s/data/structural/labels/%s_%s_labels.txt'%(
                                    os.path.expanduser('~'), brain[0], hemi), brain[0])
data2_roi_labels, data2_roi_verts = load_rois('%s/data/structural/labels/%s_%s_labels.txt'%(
                                    os.path.expanduser('~'), brain[1], hemi), brain[1])
for group in groups:
    data1 = load_structural('%s/data/structural/baseline_%s%s_SA_%s_lt18.csv' % (os.path.expanduser('~'), brain[0], hemi, group))
    data2 = load_structural('%s/data/structural/baseline_%s%s_SA_%s_lt18.csv' % (os.path.expanduser('~'), brain[1], hemi, group))
    Xs.append(construct_matrix(data1, data1_roi_verts, brain[0]))
    Ys.append(construct_matrix(data2, data2_roi_verts, brain[1]))

# now, Xs and Ys have the baseline for group1, then for group2
num_subjs1 = Xs[0].shape[0]
num_subjs2 = Xs[1].shape[0]

base_G1 = np.empty([Xs[0].shape[1], Ys[0].shape[1], num_perms])
base_G2 = np.empty([Xs[0].shape[1], Ys[0].shape[1], num_perms])
for i in range(num_perms):
    print i, '/', num_perms

    # combine the subjects, but keeping their order the same in each structural matrix
    subj_labels = np.random.permutation(num_subjs1 + num_subjs2)
    subj_groups = [range(num_subjs1), [s+num_subjs1 for s in range(num_subjs2)]]

    Xbase = np.concatenate((Xs[0], Xs[1]), axis=0)[subj_labels, :]
    Ybase = np.concatenate((Ys[0], Ys[1]), axis=0)[subj_labels, :]
    permXs = []
    permYs = []
    # make Xs and Ys in the format g1base, g2base
    for group in subj_groups:
        permXs.append(Xbase[group, :])
        permYs.append(Ybase[group, :])
    base_G1[:,:,i] = get_correlations(permXs[0], permYs[0])
    base_G2[:,:,i] = get_correlations(permXs[1], permYs[1])
perm_diff_base = base_G2 - base_G1

# now we compute the actual differences, and find out where in the distribution they lie
base_G1 = get_correlations(Xs[0], Ys[0])
base_G2 = get_correlations(Xs[1], Ys[1])
diff_base = base_G2 - base_G1
pvals = np.empty_like(diff_base)
for x in range(pvals.shape[0]):
    for y in range(pvals.shape[1]):
        stat = np.sort(perm_diff_base[x, y, :])
        pvals[x, y] = np.nonzero(stat < diff_base[x, y])[0][-1]/float(num_perms)

pl.figure()
ax3 = pl.imshow(pvals, interpolation='none');
pl.colorbar(shrink=.8);
pl.title('Significance of %s - %s (baseline)' % (groups[1], groups[0]))
pl.xticks(range(pvals.shape[1]), data2_roi_labels ,rotation='vertical')
pl.yticks(range(pvals.shape[0]), data1_roi_labels)
pl.clim(0, .05)
pl.show(block=False)

print pvals

for x in range(pvals.shape[0]):
    for y in range(pvals.shape[1]):
        if pvals[x,y]<.05:
            print '=== %s to %s (%s)===' % (data2_roi_labels[y], data1_roi_labels[x], hemi)
            print 'delta(%s) = %.2f, delta(%s) = %.2f, diff = %.2f' % (
                    groups[1], base_G2[x,y], groups[0], base_G1[x,y], diff_base[x,y])
