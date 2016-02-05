''' Checks whether there is a group difference in the seed connectivity '''

import mne
import numpy as np
from scipy import stats, sparse
import os
home = os.path.expanduser('~')
import sys

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

def output_results(clusters,pvalues,fname):
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
if len(sys.argv)>1:
    data_dir = home + '/data/results/meg_Yeo/seeds/%s/'%sys.argv[1]
    my_test = sys.argv[2]
# data_dir = home + '/data/results/meg_Yeo/seeds/net1_lMidOccipital/'
# my_test = 'onlyNVs'
thresh = .95
nperms = 5000
dist = 5   # distance between voxels to be considered connected (mm)
alphas = [.05, .01]

fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid3 = open(g3_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
g3 = [line.rstrip() for line in fid3]

print 'g1 =',g1_fname
print 'g2 =',g2_fname
print 'g3 =',g3_fname

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
        elif s in g3:
            g3_data[bidx].append(data.T)
            if bidx==0:
                g3_subjs.append(s)

all_ps = []
all_clusters = []
for bidx, band in enumerate(bands):
    print band
    X = np.arctanh(np.array(g1_data[bidx]))
    Y = np.arctanh(np.array(g2_data[bidx]))
    Z = np.arctanh(np.array(g3_data[bidx]))
    
    if my_test=='includeAll':
        all_data = np.vstack([X,Y,Z])
    elif my_test=='onlyNVs':
        all_data = X

    n = all_data.shape[0]
    # two-tailed
    t_thresh = -stats.distributions.t.ppf((1-thresh)/2, n-1)
    # # single-tailed
    # t_thresh = -stats.distributions.t.ppf((1-thresh), n-1)
    T_obs, clusters, p_values, H0 = \
    mne.stats.spatio_temporal_cluster_1samp_test(X = all_data, n_jobs=2, threshold=t_thresh, connectivity=connectivity, tail=0, n_permutations=nperms, verbose=True)

    output_results(clusters,p_values,'noContrast_%s_%dto%d'%(my_test,band[0],band[1]))

    all_ps.append(p_values)
    all_clusters.append(clusters)

    # two-sided
    P_obs = stats.t.sf(np.abs(T_obs), n-1)*2
    idx = ~np.isnan(P_obs)
    for a in alphas:
        reject_fdr, pval_fdr = mne.stats.fdr_correction(P_obs[idx], alpha=a, method='indep')
        if np.sum(pval_fdr<a) > 0:
            # if we have any good voxels left, put them in their original positions
            pvals = P_obs.copy()
            pvals[idx] = 1-pval_fdr
            pvals[~idx] = 0
            # make .nii with p-values
            fname = data_dir+'noContrast_%s_%dto%d'%(my_test,band[0],band[1])+'_a%.2ft%.2fd%dFDR'%(a,thresh,dist)
            write2afni(pvals,fname,resample=True)
