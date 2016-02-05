''' Checks whether there is a group difference in the seed connectivity '''

import mne
import numpy as np
from scipy import stats, sparse
import os
home = os.path.expanduser('~')


def write2afni(vals, fname):
    data = np.genfromtxt(home+'/sam/voxelsInROIs.txt', delimiter=' ')
    # only keep i,j,k and one column for data
    data[:,3:] = 0
    for i, d in enumerate(vals):
        data[:,3+i] = d
    np.savetxt(fname, data, fmt='%.2f', delimiter=' ', newline='\n')
    os.system('cat '+fname+ ' | 3dUndump -master '+home+'/sam/TTatlas555+tlrc -ijk -datum float -prefix '+fname+' -overwrite -')

def count_good_sources(voxels, num_print):
    areas = np.load(home+'/sam/areas.npy')[()]
    res = np.load(home+'/sam/rois.npz')
    rois = list(res['rois'])
    roi_voxels = list(res['roi_voxels'])
    roi_score = np.zeros([len(rois)])
    for idx, vox in enumerate(roi_voxels):
        for v in voxels:
            if v in vox:
                roi_score[idx] += 1
    best_rois = np.argsort(-roi_score)[:num_print]
    for r in best_rois:
        if roi_score[r] > 0:
            if rois[r]==151:
                roi_name='Putamen'
                hemi=1
            elif rois[r]==135:
                roi_name='VentralLateralNucleus'
                hemi=1
            elif rois[r]==351:
                roi_name='Putamen'
                hemi=0
            elif rois[r]==333:
                roi_name='Pulvinar'
                hemi=0
            elif rois[r]==325:
                roi_name='Caudate body'
                hemi=0
            else:
                ba = [key for key, val in areas.iteritems() if rois[r] in val][0]
                hemi = areas[ba].index(rois[r])
                roi_name = 'BA%d'%ba
            print '%s-%d: %d sources, %.2f of ROI, %.2f of significant sources'%(roi_name, hemi, roi_score[r], roi_score[r]/len(roi_voxels[r]), roi_score[r]/len(voxels))


def do_test(d1, d2, comp):
    t_threshold = -stats.distributions.t.ppf(p_thresh / 2., d1.shape[0]+d2.shape[0]-1)
    T_obs, clusters, cluster_p_values, H0 = mne.stats.spatio_temporal_cluster_test([d1, d2], n_jobs=5, threshold=t_threshold, n_permutations=4096, verbose=False, connectivity=sconn)
    good_cluster_inds = np.where(cluster_p_values < alpha)[0]
    print '%s: good clusters: %d'%(comp, len(good_cluster_inds))
    if len(good_cluster_inds)>0:
        vox = np.zeros(nfeats)
        vox[delme] = 1
        remain = np.nonzero(vox==0)[0]
        for i, ind in enumerate(good_cluster_inds):
            print '--- Cluster %d (%.2f)---'%(i+1,cluster_p_values[ind])
            in_cluster = remain[clusters[ind][1]]
            count_good_sources(in_cluster, 5)


bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
g1_fname = '/Users/sudregp/data/meg/nv_subjs.txt'
g2_fname = '/Users/sudregp/data/meg/persistent_subjs.txt'
g3_fname = '/Users/sudregp/data/meg/remitted_subjs.txt'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = '/Users/sudregp/data/meg/sam/seed/'
p_thresh = .05  # pvalue threshold for single sources
alpha = .1  # cluster alpha
near_voxels=5  # limit the neighbors to the 5 closest sources
seed = [1, -44, 3]
seed_name = 'mPFC'
# seed = [ -14, 55, 25]
# seed_name = 'pCC'
# seed = [-8, -1, 38]
# seed_name = 'dACC'
# seed = [-46, -16, 5]
# seed_name = 'rIFG'
# seed = [-32, -40, 27]
# seed_name = 'rMFG' 

coord = np.genfromtxt(home + '/sam/targetsInTLR.txt', delimiter=' ', skip_header=1)
dist = np.sqrt((coord[:,0] - seed[0])**2 + (coord[:,1] - seed[1])**2 + (coord[:,2] - seed[2])**2)
seed_src = np.argmin(dist)
print 'Seed src: %d, Distance to seed: %.2fmm'%(seed_src, np.min(dist))

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid3 = open(g3_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
g3 = [line.rstrip() for line in fid3]


print 'g1 =',g1_fname
print 'g2 =',g2_fname
print 'g3 =',g3_fname

fid = open('/Users/sudregp/tmp/u.csv','w')

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
for s in subjs:
    if s not in ['WZYXTRYY'] or (s not in ['WZYXTRYY'] and seed_name=='mPFC'):
        fname = data_dir + '%s_%s_connectivity.npy'%(s,seed_name)
        conn = np.load(fname)[()]
        for b in range(len(bands)):
            data = conn[:,b]
            if s in g1:
                g1_data[b].append(data.T)
                if b==0:
                    g1_subjs.append(s)
            elif s in g2:
                g2_data[b].append(data.T)
                if b==0:
                    g2_subjs.append(s)
            elif s in g3:
                g3_data[b].append(data.T)
                if b==0:
                    g3_subjs.append(s)

# let's create the connectivity square matrix
nfeats = conn.shape[0]
connectivity=np.zeros([nfeats, nfeats])
for i in range(nfeats):
    # find the distance from i to all other sources
    dist = np.sqrt((coord[:,0] - coord[i,0])**2 + (coord[:,1] - coord[i,1])**2 + (coord[:,2] - coord[i,2])**2)
    closest_sources = np.argsort(dist)
    # need to account for the source itself, which is 0 distance
    for j in closest_sources[1:(near_voxels+1)]:
        connectivity[i,j] = 1
    
score=0
print nfeats, 'connections'
print seed
for b in range(len(bands)):
    print bands[b]
    X = np.array(g1_data[b])
    Y = np.array(g2_data[b])
    Z = np.array(g3_data[b])
    res = []
    # remove features that have nans
    delme = np.unique(np.nonzero(np.isnan(np.vstack([X,Y,Z])))[1])
    delme = np.hstack([delme, seed_src])
    X = np.delete(X, delme, axis=1)
    Y = np.delete(Y, delme, axis=1)
    Z = np.delete(Z, delme, axis=1)

    X = X.reshape((X.shape[0],1,X.shape[1]))
    Y = Y.reshape((Y.shape[0],1,Y.shape[1]))
    Z = Z.reshape((Z.shape[0],1,Z.shape[1]))

    myconn = connectivity.copy()
    myconn = np.delete(myconn, delme, axis=0)
    myconn = np.delete(myconn, delme, axis=1)
    sconn = sparse.coo_matrix(myconn)

    do_test(X,Y,'nvVSper')
    do_test(X,Z,'nvVSrem')
    do_test(Y,Z,'perVSrem')


n1 = len(g1_data[0])
n2 = len(g2_data[0])
n3 = len(g3_data[0])
print 'size1 =', n1
print 'size2 =', n2
print 'size3 =', n3
print score
