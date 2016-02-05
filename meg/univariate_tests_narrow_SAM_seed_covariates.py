''' Checks whether there is a difference in the seed connectivity using OLS with covariates '''

import mne
import numpy as np
from scipy import stats, sparse
import os
home = os.path.expanduser('~')
import sys
import pandas as pd
import statsmodels.formula.api as smf


def linreg(*args):
    X = args[0]
    nfeats = X.shape[1]
    my_stats = []
    for i in range(nfeats):
        vec = X[:, i]
        keep = ~np.isnan(vec)
        # 2-tailed p-value by default
        my_stats.append(1-stats.pearsonr(sx[keep], vec[keep])[1])
    my_stats = np.array(my_stats)
    # might not be necessary... It doesn't (tested), but nice to see output with correct min and max, so let's leave it this way
    my_stats[np.isnan(my_stats)] = np.nanmin(my_stats)
    return my_stats


def write2afni(vals, fname, resample=False):
    data = np.genfromtxt(home + '/data/meg/sam_narrow_5mm/voxelsInBrain.txt', delimiter=' ')
    # only keep i,j,k and one column for data
    data = data[:, :4]
    # 3dUndump can only create files with one subbrick
    data[:, 3] = vals
    np.savetxt(fname+'.txt', data, fmt='%.2f', delimiter=' ', newline='\n')
    os.system('cat ' + fname + '.txt | 3dUndump -master ' + home + '/data/meg/sam_narrow_5mm/TT_N27_555+tlrc -ijk -datum float -prefix ' + fname + ' -overwrite -')
    # if asked to resample, put it back to TT_N27 grid and remove everything that lies outside the anatomy
    if resample:
        os.system('3dresample -inset '+fname+'+tlrc -prefix '+fname+'_upsampled -master '+home+'/data/meg/sam_narrow_5mm/TT_N27+tlrc -rmode NN')
        os.system('3dcalc -prefix '+fname+'_upsampled+tlrc -overwrite -a '+fname+'_upsampled+tlrc -b '+data_dir+'anat_mask+tlrc -expr \'a*b\'')


def output_results(clusters, pvalues, fname, thresh):
    for alpha in alphas:
        good_clusters = [k for k in range(len(pvalues)) if pvalues[k] < alpha]
        print 'Found %d good clusters at %.2f' % (len(good_clusters), alpha)
        if len(good_clusters) > 0:
            vals = np.zeros([nfeats])
            cnt = 1
            for c in good_clusters:
                vals[clusters[c][1]] = cnt
                cnt += 1
            write2afni(vals, data_dir + fname + '_a%.2ft%.2fd%dp%d' % (alpha, thresh, dist, nperms))

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
gf_fname = home + '/data/meg/gf.csv'
if len(sys.argv) > 1:
    data_dir = home + '/data/results/meg_Yeo/seeds/%s/' % sys.argv[1]
    my_test = sys.argv[2]
# data_dir = home+'/data/results/meg_Yeo/seeds/net1_lMidOccipital/'
# my_test = 'inatt'

# for a single connection to be good, higher the better
p_threshold = [.99]  # [.95, .99]
nperms = 5000
njobs = 4
dist = 5   # distance between voxels to be considered connected (mm)
alphas = [.05]  # , .01]

gf = pd.read_csv(gf_fname)

print 'Calculating neighboring voxels...'
vox_pos = np.genfromtxt(home + '/data/meg/sam_narrow_5mm/brainTargetsInTLR.txt', skip_header=1)
nfeats = vox_pos.shape[0]
edges = np.zeros([nfeats, nfeats])
for i in range(nfeats):
    edges[i, :] = np.sqrt((vox_pos[:, 0] - vox_pos[i, 0]) ** 2 + (vox_pos[:, 1] - vox_pos[i, 1]) ** 2 + (vox_pos[:, 2] - vox_pos[i, 2]) ** 2)
edges[:] = np.less_equal(edges, dist)
connectivity = sparse.coo_matrix(edges)

for bidx, band in enumerate(bands):
    print 'Loading data...', band
    ds_data = np.load(data_dir + '/correlations_%d-%d.npy' % (band[0], band[1]))[()]
    # just making sure they're in the same order
    subjs = []
    data = []
    for s, d in ds_data.iteritems():
        data.append(d.T)
        subjs.append(s)
    X = np.arctanh(np.array(data).squeeze())

    # the order of subjects in data is the same as in subjs
    # let's find that order in the gf and resort it
    idx = [np.nonzero(gf.maskid == s)[0][0] for s in subjs]
    gf = gf.iloc[idx]

    # let's grab the residual nows
    print 'Calculating residuals...'
    col_names = ['v%d' % i for i in range(nfeats)]
    # uses the same index so we don't have issues concatenating later
    data_df = pd.DataFrame(X, columns=col_names, index=gf.index, dtype=float)
    df = pd.concat([gf, data_df], axis=1)
    Y_resid = np.empty_like(X)
    Y_resid[:] = np.nan  # this way we keep the nan entries as is
    for v in range(nfeats):
        keep = np.nonzero(~np.isnan(df['v%d' % v]))[0]
        est = smf.ols(formula='v%d ~ age + gender' % v, data=df.iloc[keep]).fit()
        Y_resid[np.array(keep), v] = est.resid

    # reshape it to work with the MNE function
    Y_resid = Y_resid.reshape([Y_resid.shape[0], 1, Y_resid.shape[1]])

    # careful with the selection based on iloc, to keep the same index as the data matrix
    groups = gf.group.tolist()
    # tail=1 because we use 1-pvalue as threshold
    for thresh in p_threshold:
        if my_test == 'inatt':
            idx = [i for i, v in enumerate(groups)
                   if v in ['remission', 'persistent']]
            sx = np.array(df.iloc[idx].inatt)
        elif my_test == 'hi':
            idx = [i for i, v in enumerate(groups)
                   if v in ['remission', 'persistent']]
            sx = np.array(df.iloc[idx].hi)
        elif my_test == 'total':
            idx = [i for i, v in enumerate(groups)
                   if v in ['remission', 'persistent']]
            sx = np.array(df.iloc[idx].total)
        elif my_test == 'inattWithNVs':
            idx = range(Y_resid.shape[0])
            sx = np.array(df.inatt)
        elif my_test == 'hiWithNVs':
            idx = range(Y_resid.shape[0])
            sx = np.array(df.hi)
        elif my_test == 'totalWithNVs':
            idx = range(Y_resid.shape[0])
            sx = np.array(df.total)

        stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test([Y_resid[idx]], n_jobs=njobs, threshold=thresh, connectivity=connectivity, tail=1, stat_fun=linreg, n_permutations=nperms, verbose=True)

        output_results(clusters, p_values,
                       'RESID_%s_%dto%d' % (my_test, band[0], band[1]),
                       thresh)
