import numpy as np
import os
import scipy
import pylab as pl
from scipy import stats

thalamus_label_names = ['LGN', 'MGN', 'Anterior nuclei', 'Central nuclei', 'Lateral Dorsal', 'Lateral Posterior', 'Medial Dorsal', 'Pulvinar', 'VA', 'VL', 'VP']
striatum_label_names = []

def load_structural(fname):
    data = np.genfromtxt(fname, delimiter=',')
    # removing first column and first row, because they're headers
    data = scipy.delete(data, 0, 1)
    data = scipy.delete(data, 0, 0)
    # format it to be subjects x variables
    data = data.T
    return data


def load_rois(fname):
    roi_vertices = []
    labels = np.genfromtxt(fname)
    rois = np.unique(labels)
    for r in rois:
        roi_vertices.append(np.nonzero(labels == r)[0])
    return rois, roi_vertices


def construct_matrix(data, rois):
    num_subjects = data.shape[0]
    Y = np.zeros([num_subjects, len(rois)])
    for r, roi in enumerate(rois):
        Y[:, r] = stats.nanmean(data[:, roi], axis=1)
    return Y


def plot_correlations(corr):
    pl.figure()
    pl.imshow(corr, interpolation='none')
    pl.colorbar()
    # ONLY WORKS FOR THE RIGHT SIDE!
    pl.xticks(range(corr.shape[1]),['Anterior nuclei', 'Central nuclei', 'Lateral Dorsal', 'Lateral Posterior', 'Medial Dorsal', 'Pulvinar', 'VA', 'VL', 'VP'],rotation='vertical')
    pl.yticks(range(corr.shape[0]),['Nucleus Accumbens', 'Pre Putamen', 'Caudate-Putamen Medial Intersection', 'Pre Caudate', 'Post Caudate', 'Post Putamen'])
    pl.show(block=False)
    return pl.gcf


def do_bootstrapping(data1, data2, num_perms):
    num_subjects = data1.shape[0]

    corr = np.empty([data1.shape[1], data2.shape[1], num_perms])
    pvals = np.empty([data1.shape[1], data2.shape[1], num_perms])
    for perm in range(num_perms):
        print perm+1, '/', num_perms
        boot_idx = np.random.random_integers(0, num_subjects-1, num_subjects)
        X = data1[boot_idx, :]
        Y = data2[boot_idx, :]
        for x in range(X.shape[1]):
            for y in range(Y.shape[1]):
                corr[x, y, perm], pvals[x, y, perm] = scipy.stats.pearsonr(X[:, x], Y[:, y])
    return corr


groups = ['NV', 'ADHD']
num_perms = 10000
corrs = []
pvals = []
boot_corrs = []
out_fname = os.path.expanduser('~') + '/data/results/structural/pearson_rois_thalamus_striatum_baseLT18_MATCH5'
for group in groups:
    data1 = load_structural(os.path.expanduser('~') + '/data/structural/baseline_striatumR_SA_%s_QCCIVETlt35_QCSUBePASS_MATCH5_lt18.csv' % group)
    data2 = load_structural(os.path.expanduser('~') + '/data/structural/baseline_thalamusR_SA_%s_QCCIVETlt35_QCSUBePASS_MATCH5_lt18.csv' % group)
    data1_roi_labels, data1_roi_verts = load_rois(os.path.expanduser('~') + '/data/structural/labels/striatum_right_labels.txt')
    data2_roi_labels, data2_roi_verts = load_rois(os.path.expanduser('~') + '/data/structural/labels/thalamus_right_morpho_labels_test.txt')

    X = construct_matrix(data1, data1_roi_verts)
    Y = construct_matrix(data2, data2_roi_verts)

    corr = np.empty([X.shape[1], Y.shape[1]])
    pval = np.empty([X.shape[1], Y.shape[1]])
    for x in range(X.shape[1]):
        print str(x+1) + '/' + str(X.shape[1])
        for y in range(Y.shape[1]):
            corr[x, y], pval[x, y] = stats.pearsonr(X[:, x], Y[:, y])

    corrs.append(corr)
    pvals.append(pval)

    plot_correlations(corr)
    pl.title('%s, n=%d'%(group, X.shape[0]))
    pl.draw()

    # checking p-values of the differences
    boot_corrs.append(do_bootstrapping(X, Y, num_perms))

diff_pvals = np.empty_like(corr)
dcorr = boot_corrs[1] - boot_corrs[0]
for x in range(X.shape[1]):
    for y in range(Y.shape[1]):
        stat = np.sort(dcorr[x, y])
        diff_pvals[x, y] = np.nonzero(stat < 0)[0][-1]/float(num_perms)
# invert the values for which 0 is in the wrong side of the distribution (i.e. the difference between the groups is still significant, but it's just not 1-0)
wrong_side = diff_pvals>.5
diff_pvals[wrong_side] = 1 - diff_pvals[wrong_side]

plot_correlations(diff_pvals)
pl.title('diffs %s vs %s'%(groups[0], groups[1]))
pl.clim(0,.05)
pl.draw()
# remember to use pl.ion()! to turn interactive session on

np.savez(out_fname, corrs=corrs, pvals=pvals, boot_corrs=boot_corrs, groups=groups)
