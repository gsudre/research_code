''' Checks whether there is a difference in the MEG activity during task '''

import mne
import numpy as np
from scipy import stats, sparse
import os
home = os.path.expanduser('~')
import sys
import pandas as pd
import glob
import nibabel as nb


def linreg(*args):
    X = args[0]
    nfeats = X.shape[1]
    my_stats = []
    for i in range(nfeats):
        vec = X[:, i]
        keep = ~np.isnan(vec)
        # 2-tailed p-value by default
        my_stats.append(1 - stats.pearsonr(sx[keep], vec[keep])[1])
    my_stats = np.array(my_stats)
    # might not be necessary... It doesn't (tested), but nice to see output with correct min and max, so let's leave it this way
    my_stats[np.isnan(my_stats)] = np.nanmin(my_stats)
    return my_stats


def group_comparison(*args):
    if len(args) == 2:
        my_stats = 1 - stats.f_oneway(args[0], args[1])[1]
    else:
        my_stats = 1 - stats.f_oneway(args[0], args[1], args[2])[1]
    # might not be necessary... It doesn't (tested), but nice to see output with correct min and max, so let's leave it this way
    my_stats[np.isnan(my_stats)] = np.nanmin(my_stats)
    return my_stats


def output_results(clusters, pvalues, fname, thresh):
    for alpha in alphas:
        good_clusters = [k for k in range(len(pvalues)) if pvalues[k] < alpha]
        print 'Found %d good clusters at %.2f' % (len(good_clusters), alpha)


if len(sys.argv) > 1:
    my_test = sys.argv[1]
    ltype = sys.argv[2]
    cond = sys.argv[3]
    njobs = int(sys.argv[4])
    after_zero = bool(float(sys.argv[5]))
else:
    my_test = 'ssrt'
    ltype = 'dSPM_base'
    cond = 'STI-correct'
    njobs = 1
    after_zero = True

data_dir = home + '/data/meg/analysis/stop/source_volume_at_red/nii_tlrc/'
# data_dir = '/mnt/shaw/MEG_data/analysis/stop/source_volume_at_red/nii_tlrc/'
res_dir = home + '/data/results/stop_sources_volume_at_red/'
gf_fname = home + '/data/meg/gf.csv'
# for a single voxel to be good, higher the better
p_threshold = [.95, .99]
nperms = 1000
dist = 5
alphas = [.05, .01]

print 'Calculating neighboring voxels...'
vox_pos = np.genfromtxt(data_dir + '/mask.txt')
nfeats = vox_pos.shape[0]
edges = np.zeros([nfeats, nfeats])
for i in range(nfeats):
    edges[i, :] = np.sqrt((vox_pos[:, 3] - vox_pos[i, 3]) ** 2 + (vox_pos[:, 4] - vox_pos[i, 4]) ** 2 + (vox_pos[:, 5] - vox_pos[i, 5]) ** 2)
edges[:] = np.less_equal(edges, dist)
connectivity = sparse.coo_matrix(edges)

gf = pd.read_csv(gf_fname)

print 'Loading data...'
files = glob.glob(data_dir + '*%s_%s.nii' % (cond, ltype))
X = []
gf_loc = []
for fname in files:
    # exclude due to psychotropic factors
    if fname.find('WCEYBWMO') < 0:
        img = nb.load(fname)
        if ltype.find('DICSepochs') >= 0:
            ntimes = 1
        elif after_zero:
            ntimes = 19
        else:
            ntimes = 29
        subj_data = np.zeros([nfeats, ntimes])
        for i in range(nfeats):
            if img.get_data().ndim > 3:
                subj_data[i, :] = img.get_data()[int(vox_pos[i, 0]),
                                                 int(vox_pos[i, 1]),
                                                 int(vox_pos[i, 2]),
                                                 (img.shape[-1] - ntimes):]
            else:
                subj_data[i, :] = img.get_data()[int(vox_pos[i, 0]),
                                                 int(vox_pos[i, 1]),
                                                 int(vox_pos[i, 2])]
        X.append(subj_data)
        subj = fname.split('/')[-1].split('_')[0]
        gf_loc.append(np.nonzero(gf.maskid == subj)[0][0])
if len(X) != len(gf_loc):
    print 'Mismatch between subject data and gf!'

# re-sort subject order in gf to match X
gf = gf.iloc[gf_loc]

for thresh in p_threshold:
    if my_test == 'nvVSper':
        g0 = [X[i].T for i, group in enumerate(gf.group) if group == 'NV']
        g1 = [X[i].T for i, group in enumerate(gf.group) if group == 'persistent']
        data = [np.array(g0), np.array(g1)]
        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test(data, n_jobs=njobs,
                                                   threshold=thresh,
                                                   connectivity=connectivity,
                                                   stat_fun=group_comparison,
                                                   tail=1,
                                                   n_permutations=nperms,
                                                   verbose=True)
    elif my_test == 'nvVSrem':
        g0 = [X[i].T for i, group in enumerate(gf.group) if group == 'NV']
        g1 = [X[i].T for i, group in enumerate(gf.group) if group == 'remission']
        data = [np.array(g0), np.array(g1)]
        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test(data, n_jobs=njobs,
                                                   threshold=thresh,
                                                   connectivity=connectivity,
                                                   stat_fun=group_comparison,
                                                   tail=1,
                                                   n_permutations=nperms,
                                                   verbose=True)
    elif my_test == 'perVSrem':
        g0 = [X[i].T for i, group in enumerate(gf.group) if group == 'persistent']
        g1 = [X[i].T for i, group in enumerate(gf.group) if group == 'remission']
        data = [np.array(g0), np.array(g1)]
        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test(data, n_jobs=njobs,
                                                   threshold=thresh,
                                                   connectivity=connectivity,
                                                   stat_fun=group_comparison,
                                                   tail=1,
                                                   n_permutations=nperms,
                                                   verbose=True)
    elif my_test == 'nvVSadhd':
        g0 = [X[i].T for i, group in enumerate(gf.group) if group == 'NV']
        g1 = [X[i].T for i, group in enumerate(gf.group) if group in ['persistent', 'remission']]
        data = [np.array(g0), np.array(g1)]
        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test(data, n_jobs=njobs,
                                                   threshold=thresh,
                                                   connectivity=connectivity,
                                                   stat_fun=group_comparison,
                                                   tail=1,
                                                   n_permutations=nperms,
                                                   verbose=True)
    elif my_test == 'anova':
        g0 = [X[i].T for i, group in enumerate(gf.group) if group == 'persistent']
        g1 = [X[i].T for i, group in enumerate(gf.group) if group == 'remission']
        g2 = [X[i].T for i, group in enumerate(gf.group) if group == 'NV']
        data = [np.array(g0), np.array(g1), np.array(g2)]
        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test(data, n_jobs=njobs,
                                                   threshold=thresh,
                                                   connectivity=connectivity,
                                                   stat_fun=group_comparison,
                                                   tail=1,
                                                   n_permutations=nperms,
                                                   verbose=True)
    elif my_test == 'inatt':
        g0 = [X[i].T for i, group in enumerate(gf.group) if group in ['persistent', 'remission']]
        sx = [s for g, s in zip(gf.group, gf.inatt) if g in ['persistent', 'remission']]
        sx = np.array(sx)
        data = [np.array(g0)]
        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test(data, n_jobs=njobs,
                                                   threshold=thresh,
                                                   connectivity=connectivity,
                                                   stat_fun=linreg,
                                                   tail=1,
                                                   n_permutations=nperms,
                                                   verbose=True)
    elif my_test == 'hi':
        g0 = [X[i].T for i, group in enumerate(gf.group) if group in ['persistent', 'remission']]
        sx = [s for g, s in zip(gf.group, gf.hi) if g in ['persistent', 'remission']]
        sx = np.array(sx)
        data = [np.array(g0)]
        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test(data, n_jobs=njobs,
                                                   threshold=thresh,
                                                   connectivity=connectivity,
                                                   stat_fun=linreg,
                                                   tail=1,
                                                   n_permutations=nperms,
                                                   verbose=True)
    elif my_test == 'total':
        g0 = [X[i].T for i, group in enumerate(gf.group) if group in ['persistent', 'remission']]
        sx = [s1 + s2 for g, s1, s2 in zip(gf.group, gf.inatt, gf.hi) if g in ['persistent', 'remission']]
        sx = np.array(sx)
        data = [np.array(g0)]
        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test(data, n_jobs=njobs,
                                                   threshold=thresh,
                                                   connectivity=connectivity,
                                                   stat_fun=linreg,
                                                   tail=1,
                                                   n_permutations=nperms,
                                                   verbose=True)
    elif my_test == 'ssrt':
        g0 = [X[i].T for i, group in enumerate(gf.group) if group in ['persistent', 'remission']]
        sx = [s for g, s in zip(gf.group, gf.ssrt) if g in ['persistent', 'remission']]
        sx = np.array(sx)
        data = [np.array(g0)]
        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test(data, n_jobs=njobs,
                                                   threshold=thresh,
                                                   connectivity=connectivity,
                                                   stat_fun=linreg,
                                                   tail=1,
                                                   n_permutations=nperms,
                                                   verbose=True)
    elif my_test == 'inattWithNVs':
        sx = np.array(gf.inatt)
        data = [np.swapaxes(np.array(X), 2, 1)]
        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test(data, n_jobs=njobs,
                                                   threshold=thresh,
                                                   connectivity=connectivity,
                                                   stat_fun=linreg,
                                                   tail=1,
                                                   n_permutations=nperms,
                                                   verbose=True)
    elif my_test == 'hiWithNVs':
        sx = np.array(gf.hi)
        data = [np.swapaxes(np.array(X), 2, 1)]
        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test(data, n_jobs=njobs,
                                                   threshold=thresh,
                                                   connectivity=connectivity,
                                                   stat_fun=linreg,
                                                   tail=1,
                                                   n_permutations=nperms,
                                                   verbose=True)
    elif my_test == 'totalWithNVs':
        sx = np.array(gf.inatt) + np.array(gf.hi)
        data = [np.swapaxes(np.array(X), 2, 1)]
        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test(data, n_jobs=njobs,
                                                   threshold=thresh,
                                                   connectivity=connectivity,
                                                   stat_fun=linreg,
                                                   tail=1,
                                                   n_permutations=nperms,
                                                   verbose=True)
    elif my_test == 'ssrtWithNVs':
        sx = np.array(gf.ssrt)
        data = [np.swapaxes(np.array(X), 2, 1)]
        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test(data, n_jobs=njobs,
                                                   threshold=thresh,
                                                   connectivity=connectivity,
                                                   stat_fun=linreg,
                                                   tail=1,
                                                   n_permutations=nperms,
                                                   verbose=True)

    for alpha in alphas:
        good_clusters = [k for k in range(len(p_values)) if p_values[k] < alpha]
        print 'Found %d good clusters at %.2f' % (len(good_clusters), alpha)
        if after_zero:
            fname = '%s_%s_%s_afterZero_p%.2fa%.2f_perms%d.npz' % (my_test,
                                                                   ltype,
                                                                   cond,
                                                                   thresh,
                                                                   alpha,
                                                                   nperms)
        else:
            fname = '%s_%s_%s_p%.2fa%.2f_perms%d.npz' % (my_test,
                                                         ltype,
                                                         cond,
                                                         thresh,
                                                         alpha,
                                                         nperms)
        fname = res_dir + fname
        if len(good_clusters) > 0:
            my_clusters = [clusters[c] for c in good_clusters]
            my_pvals = [p_values[c] for c in good_clusters]
            np.savez(fname, clusters=my_clusters, p_values=my_pvals,
                     stat_obs=stat_obs)
