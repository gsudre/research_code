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


g1_fname = home + '/data/fmri/joel_nvs.txt'
g2_fname = home + '/data/fmri/joel_persistent.txt'
g3_fname = home + '/data/fmri/joel_remission.txt'
subjs_fname = home + '/data/fmri/joel_all.txt'

if len(sys.argv)>1:
    data_dir = home + '/data/results/fmri_Yeo/seeds/%s/'%sys.argv[1]
# data_dir = home + '/data/results/fmri_Yeo/seeds/net1_lMidOccipital/'

thresh = .99
nperms = 100
dist = 5   # distance between voxels to be considered connected (mm)
alphas = [.05, .01]

fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid3 = open(g3_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
g3 = [line.rstrip() for line in fid3]
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

g1_data = []
g2_data = []
g3_data = []
g1_subjs=[]
g2_subjs=[]
g3_subjs=[]

print 'Loading data...'
data = np.genfromtxt(data_dir + '/joel_all_corr_downsampled.txt')

vox_pos = data[:,3:6]
nfeats = vox_pos.shape[0]
edges = np.zeros([nfeats,nfeats])
for i in range(nfeats):
    edges[i,:] = np.sqrt((vox_pos[:,0] - vox_pos[i,0])**2 + (vox_pos[:,1] - vox_pos[i,1])**2 + (vox_pos[:,2] - vox_pos[i,2])**2)
edges[:] = np.less_equal(edges, dist)
connectivity = sparse.coo_matrix(edges)

data = data[:,6:]
cnt=0
for s in subjs:
    if s in g1:
        g1_data.append(data[:,cnt].T)
        g1_subjs.append(s)
    elif s in g2:
        g2_data.append(data[:,cnt].T)
        g2_subjs.append(s)
    elif s in g3:
        g3_data.append(data[:,cnt].T)
        g3_subjs.append(s)
    cnt+=1

all_ps = []
all_clusters = []

X = np.arctanh(np.array(g1_data)).reshape([len(g1_subjs),1,nfeats])
Y = np.arctanh(np.array(g2_data)).reshape([len(g2_subjs),1,nfeats])
Z = np.arctanh(np.array(g3_data)).reshape([len(g3_subjs),1,nfeats])

all_data = np.vstack([X,Y,Z])
n = all_data.shape[0]
t_thresh = -stats.distributions.t.ppf(thresh, n-1)
T_obs, clusters, p_values, H0 = \
mne.stats.spatio_temporal_cluster_1samp_test(X = all_data, n_jobs=2, threshold=t_thresh, connectivity=connectivity, tail=0, n_permutations=nperms, verbose=True)

output_results(clusters,p_values,'noContrast_includeAll')
