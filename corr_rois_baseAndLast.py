import numpy as np
import os
import scipy
import pylab as pl
from scipy import stats
import pdb

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


def do_bootstrapping(data1, data2, num_perms, verbose, reuse_ids=[]):
    num_subjects = data1.shape[0]

    corr = np.empty([data1.shape[1], data2.shape[1], num_perms])
    pvals = np.empty([data1.shape[1], data2.shape[1], num_perms])
    boot_ids = []
    for perm in range(num_perms):
        if verbose:
            print perm+1, '/', num_perms
        if len(reuse_ids)==0:
            boot_idx = np.random.random_integers(0, num_subjects-1, num_subjects)
        else:
            boot_idx = reuse_ids[perm, :]
        boot_ids.append(boot_idx)

        X = data1[boot_idx, :]
        Y = data2[boot_idx, :]
        for x in range(X.shape[1]):
            for y in range(Y.shape[1]):
                corr[x, y, perm], pvals[x, y, perm] = scipy.stats.pearsonr(X[:, x], Y[:, y])
    return corr


def run_bootstrap_correlations(Xs, Ys, num_perms, plot=False, verbose=False, permute=False):
# Returns the difference of correlation between X[1]*Y[1] - X[0]*Y[0] using bootstrap
    corrs = []
    pvals = []
    boot_corrs = []

    # need to define ahead of time the bootstrap indexes so we run the same ones for X[1] and X[0] (e.g. baseline and last)
    num_subjects = Xs[0].shape[0]
    boot_idx = np.random.random_integers(0, num_subjects-1, [num_perms, num_subjects])
    for X, Y in zip(Xs, Ys):
        corr = np.empty([X.shape[1], Y.shape[1]])
        pval = np.empty([X.shape[1], Y.shape[1]])
        for x in range(X.shape[1]):
            for y in range(Y.shape[1]):
                corr[x, y], pval[x, y] = stats.pearsonr(X[:, x], Y[:, y])

        corrs.append(corr)
        pvals.append(pval)

        if plot:
            plot_correlations(corr)
            pl.title('n=%d'%X.shape[0])
            pl.clim(-.2, .8)
            pl.draw()

        # checking p-values of the differences
        boot_res = do_bootstrapping(X, Y, num_perms, verbose, reuse_ids=boot_idx)
        boot_corrs.append(boot_res)

    dcorr = boot_corrs[1] - boot_corrs[0]

    return (corrs, pvals, dcorr)

####
groups = ['remission', 'persistent']
num_perms = 10000
out_fname = os.path.expanduser('~') + '/data/results/structural/pearson_rois_thalamus_striatum_baseAndLast18_RemissionVsPersistent'

# load the data for both groups, both structures
Xs = []
Ys = []
data1_roi_labels, data1_roi_verts = load_rois(os.path.expanduser('~') + '/data/structural/labels/striatum_right_labels.txt')
data2_roi_labels, data2_roi_verts = load_rois(os.path.expanduser('~') + '/data/structural/labels/thalamus_right_morpho_labels_test.txt')
for group in groups:
    data1 = load_structural(os.path.expanduser('~') + '/data/structural/baseline_striatumR_SA_%s_lt18.csv' % group)
    data2 = load_structural(os.path.expanduser('~') + '/data/structural/baseline_thalamusR_SA_%s_lt18.csv' % group)
    Xs.append(construct_matrix(data1, data1_roi_verts))
    Ys.append(construct_matrix(data2, data2_roi_verts))

    data1 = load_structural(os.path.expanduser('~') + '/data/structural/last_striatumR_SA_%s_mt18.csv' % group)
    data2 = load_structural(os.path.expanduser('~') + '/data/structural/last_thalamusR_SA_%s_mt18.csv' % group)
    Xs.append(construct_matrix(data1, data1_roi_verts))
    Ys.append(construct_matrix(data2, data2_roi_verts))

# let's compute the difference between first and last for the first group
corrs_G1, pvals_G1, diff_last_base_G1 = run_bootstrap_correlations(Xs[:2], Ys[:2], num_perms, verbose=True, plot=True)
corrs_G2, pvals_G2, diff_last_base_G2 = run_bootstrap_correlations(Xs[2:], Ys[2:], num_perms, verbose=True, plot=True)
#np.savez(out_fname, groups=groups, corrs_G1=corrs_G1, pvals_G1=pvals_G1, diff_last_base_G1=diff_last_base_G1, corrs_G2=corrs_G2, pvals_G2=pvals_G2, diff_last_base_G2=diff_last_base_G2)
