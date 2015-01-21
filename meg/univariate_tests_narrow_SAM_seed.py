''' Checks whether there is a group difference in the seed connectivity '''

import mne
import numpy as np
from scipy import stats, sparse
import os
home = os.path.expanduser('~')
import sys

def inatt_linreg(*args):
    my_inatt = np.array(inatt)
    if len(args)==2:
        X = np.vstack([args[0],args[1]])
    else:
        X = np.vstack([args[0],args[1],args[2]])
    nfeats = X.shape[1]
    my_stats = []
    for i in range(nfeats):
        vec = X[:,i]
        keep = ~np.isnan(vec)
        # 2-tailed p-value by default
        my_stats.append(1-stats.pearsonr(my_inatt[keep], vec[keep])[1])
    my_stats = np.array(my_stats)
    # might not be necessary... It doesn't (tested), but nice to see output with correct min and max, so let's leave it this way 
    my_stats[np.isnan(my_stats)] = np.nanmin(my_stats)
    return my_stats

def hi_linreg(*args):
    my_hi = np.array(hi)
    if len(args)==2:
        X = np.vstack([args[0],args[1]])
    else:
        X = np.vstack([args[0],args[1],args[2]])
    nfeats = X.shape[1]
    my_stats = []
    for i in range(nfeats):
        vec = X[:,i]
        keep = ~np.isnan(vec)
        # 2-tailed p-value by default
        my_stats.append(1-stats.pearsonr(my_hi[keep], vec[keep])[1])
    my_stats = np.array(my_stats)
    # might not be necessary... It doesn't (tested), but nice to see output with correct min and max, so let's leave it this way 
    my_stats[np.isnan(my_stats)] = np.nanmin(my_stats)
    return my_stats

def group_comparison(*args):
    if len(args)==2:
        my_stats = 1-stats.f_oneway(args[0],args[1])[1]
    else:
        my_stats = 1-stats.f_oneway(args[0],args[1],args[2])[1]
    # might not be necessary... It doesn't (tested), but nice to see output with correct min and max, so let's leave it this way 
    my_stats[np.isnan(my_stats)] = np.nanmin(my_stats)
    return my_stats

def write2afni(vals, fname, resample=True):
    data = np.genfromtxt(home+'/data/meg/sam_narrow_5mm/voxelsInBrain.txt', delimiter=' ')
    # only keep i,j,k and one column for data
    data = data[:, :4]
    # 3dUndump can only create files with one subbrick
    data[:,3] = vals
    np.savetxt(fname+'.txt', data, fmt='%.2f', delimiter=' ', newline='\n')
    os.system('cat '+fname+ '.txt | 3dUndump -master '+home+'/data/meg/sam_narrow_5mm/TTatlas555+tlrc -ijk -datum float -prefix '+fname+' -overwrite -')
    # if asked to resample, put it back to TT_N27 grid and remove everything that lies outside the anatomy
    if resample:
        os.system('3dresample -inset '+fname+'+tlrc -prefix '+fname+'_upsampled -master '+home+'/data/meg/sam_narrow_5mm/TT_N27+tlrc -rmode NN')
        os.system('3dcalc -prefix '+fname+'_upsampled+tlrc -overwrite -a '+fname+'_upsampled+tlrc -b '+data_dir+'anat_mask+tlrc -expr \'a*b\'')

def output_results(clusters,pvalues,fname,thresh):
    for alpha in alphas:
        good_clusters = [k for k in range(len(pvalues)) if pvalues[k]<alpha]
        print 'Found %d good clusters at %.2f'%(len(good_clusters),alpha)
        if len(good_clusters)>0:
            vals = np.zeros([nfeats])
            cnt = 1
            for c in good_clusters:
                vals[clusters[c][1]] = cnt
                cnt += 1
            write2afni(vals,data_dir+fname+'_a%.2ft%.2fd%dp%d'%(alpha,thresh,dist,nperms))


bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
g1_fname = home + '/data/meg/nv_subjs.txt'
g2_fname = home + '/data/meg/persistent_subjs.txt'
g3_fname = home + '/data/meg/remitted_subjs.txt'
inatt_fname = home + '/data/meg/inatt.txt'
hi_fname = home + '/data/meg/hi.txt'
if len(sys.argv)>1:
    data_dir = home + '/data/results/meg_Yeo/seeds/%s/'%sys.argv[1]
    my_test = sys.argv[2]
# data_dir = home + '/data/results/meg_Yeo/seeds/net1_lMidOccipital/'
# my_test = 'inatt'

# for a single connection to be good, higher the better
p_threshold = [.95, .99]
nperms = 5000
njobs = 4
dist = 5   # distance between voxels to be considered connected (mm)
alphas = [.05, .01]

fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid3 = open(g3_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
g3 = [line.rstrip() for line in fid3]
res = np.recfromtxt(inatt_fname, delimiter='\t')
inatt = {}
for rec in res:
    inatt[rec[0]] = rec[1]
res = np.recfromtxt(hi_fname, delimiter='\t')
hi = {}
for rec in res:
    hi[rec[0]] = rec[1]

vox_pos = np.genfromtxt(home + '/data/meg/sam_narrow_5mm/brainTargetsInTLR.txt', skip_header=1)
nfeats = vox_pos.shape[0]
edges = np.zeros([nfeats,nfeats])
for i in range(nfeats):
    edges[i,:] = np.sqrt((vox_pos[:,0] - vox_pos[i,0])**2 + (vox_pos[:,1] - vox_pos[i,1])**2 + (vox_pos[:,2] - vox_pos[i,2])**2)
edges[:] = np.less_equal(edges, dist)
connectivity = sparse.coo_matrix(edges)

g1_data = [[] for b in range(len(bands))]
g2_data = [[] for b in range(len(bands))]
g3_data = [[] for b in range(len(bands))]
g1_subjs=[]
g2_subjs=[]
g3_subjs=[]
g2_inatt = []
g2_hi = []
g3_inatt = []
g3_hi = []

for bidx, band in enumerate(bands):
    print 'Loading data...', band
    ds_data = np.load(data_dir + '/correlations_%d-%d.npy'%(band[0],band[1]))[()]
    for s, data in ds_data.iteritems():
        if s in g1:
            g1_data[bidx].append(data.T)
            if bidx==0:
                g1_subjs.append(s)
        elif s in g2:
            g2_data[bidx].append(data.T)
            if bidx==0:
                g2_subjs.append(s)
                g2_inatt.append(inatt[s])
                g2_hi.append(hi[s])
        elif s in g3:
            g3_data[bidx].append(data.T)
            if bidx==0:
                g3_subjs.append(s)
                g3_inatt.append(inatt[s])
                g3_hi.append(hi[s])

inatt = g2_inatt + g3_inatt
hi = g2_hi + g3_hi

for bidx, band in enumerate(bands):
    print band
    X = np.arctanh(np.array(g1_data[bidx]))
    Y = np.arctanh(np.array(g2_data[bidx]))
    Z = np.arctanh(np.array(g3_data[bidx]))
    
    for thresh in p_threshold:
        # tail=1 because we use 1-pvalue as threshold for everything
        if my_test=='inatt':
            n = Y.shape[0]+Z.shape[0]
            stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test([Y,Z], n_jobs=njobs, threshold=thresh, connectivity=connectivity, tail=1, stat_fun=inatt_linreg, n_permutations=nperms, verbose=True)
        # tail=1 because we use 1-pvalue as threshold for correlations
        elif my_test=='hi':
            n = Y.shape[0]+Z.shape[0]
            stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test([Y,Z], n_jobs=njobs, threshold=thresh, connectivity=connectivity, tail=1, stat_fun=hi_linreg, n_permutations=nperms, verbose=True)
        elif my_test=='nvVSper':
            n = X.shape[0]+Y.shape[0]
            stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test([X,Y], n_jobs=njobs, threshold=thresh, connectivity=connectivity, stat_fun=group_comparison, tail=1, n_permutations=nperms, verbose=True)
        elif my_test=='nvVSrem':
            n = X.shape[0]+Z.shape[0]
            stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test([X,Z], n_jobs=njobs, threshold=t_thresh, connectivity=connectivity, stat_fun=group_comparison, tail=1, n_permutations=nperms, verbose=True)
        elif my_test=='perVSrem':
            n = Y.shape[0]+Z.shape[0]
            stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test([Y,Z], n_jobs=njobs, threshold=thresh, connectivity=connectivity, stat_fun=group_comparison, tail=1, n_permutations=nperms, verbose=True)
        elif my_test=='nvVSadhd':
            ADHD = np.vstack([Y,Z])
            n = ADHD.shape[0]
            stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test([X,ADHD], n_jobs=njobs, threshold=thresh, connectivity=connectivity, stat_fun=group_comparison, tail=1, n_permutations=nperms, verbose=True)
        elif my_test=='anova':
            n = Y.shape[0]+Z.shape[0]+X.shape[0]
            stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test([X,Y,Z], n_jobs=njobs, threshold=thresh, stat_fun=group_comparison, connectivity=connectivity, tail=1, n_permutations=nperms, verbose=True)
        elif my_test=='inattWithNVs':
            n = Y.shape[0]+Z.shape[0]+X.shape[0]
            inatt = len(g1_subjs)*[0] + g2_inatt + g3_inatt
            stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test([X,Y,Z], n_jobs=njobs, threshold=thresh, connectivity=connectivity, tail=1, stat_fun=inatt_linreg, n_permutations=nperms, verbose=True)
        elif my_test=='hiWithNVs':
            n = Y.shape[0]+Z.shape[0]+X.shape[0]
            hi = len(g1_subjs)*[0] + g2_hi + g3_hi
            stat_obs, clusters, p_values, H0 = \
            mne.stats.spatio_temporal_cluster_test([X,Y,Z], n_jobs=njobs, threshold=thresh, connectivity=connectivity, tail=1, stat_fun=hi_linreg, n_permutations=nperms, verbose=True)

        output_results(clusters,p_values,'%s_%dto%d'%(my_test,band[0],band[1]),thresh)

    # P_obs = stats.t.sf(np.abs(stat_obs), n-1)*2
    # idx = ~np.isnan(P_obs)
    # for a in alphas:
    #     reject_fdr, pval_fdr = mne.stats.fdr_correction(P_obs[idx], alpha=a, method='indep')
    #     if np.sum(pval_fdr<a) > 0:
    #         # if we have any good voxels left, put them in their original positions
    #         pvals = P_obs.copy()
    #         pvals[idx] = 1-pval_fdr
    #         pvals[~idx] = 0
    #         # make .nii with p-values
    #         fname = data_dir+'%s_%dto%d'%(my_test,band[0],band[1])+'_a%.2ft%.2fd%dFDR'%(a,thresh,dist)
    #         write2afni(pvals,fname,resample=True)