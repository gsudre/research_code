''' Checks if connections inside network are different in fMRI.

Gustavo Sudre, 08/2014 '''

import numpy as np
import os
from scipy import stats
import nbs
home = os.path.expanduser('~')



hemi = [0,1]
rois = [31,32,39]
rois = [24,10,32,29,30,23,31,39,40,21,24,9] #all from Buckner
rois = [24,10,32,30,23,31,39,40,21,24,9] #all from Buckner, also in MEG
# rois = [24,31,39,21] # good results, some matching with fmri
rois = [10,40,23,21]
data_dir = home+'/data/meg/sam/'
band_names = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
bands = range(len(band_names))
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = '/Users/sudregp/data/meg/sam/'
g1_fname = home+'/data/meg/nv_subjs.txt'
g2_fname = home+'/data/meg/persistent_subjs.txt'
g3_fname = home+'/data/meg/remitted_subjs.txt'
equal_var = True
cmethod = 5
alpha = .05

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid3 = open(g3_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
g3 = [line.rstrip() for line in fid3]

areas = np.load(home+'/sam/areas.npy')[()]
res = np.load(home+'/sam/rois.npz')
roi_vals = list(res['rois'])
roi_idx = []
for r in rois:
    roi_val = areas[r]
    roi_idx.append(roi_vals.index(roi_val[0]))
    roi_idx.append(roi_vals.index(roi_val[1]))
il = np.tril_indices(len(roi_vals), k=-1)

# create correlations for each subject
g1_data = [[] for b in bands]
g2_data = [[] for b in bands]
g3_data = [[] for b in bands]
for s in subjs:
    fname = data_dir + '%s_roi_connectivity.npy'%s
    conn = np.load(fname)[()]
    for b in bands:
        band_data = conn[b][cmethod][:,:].squeeze()
        band_data = band_data[il]
        subj_data = []
        conn_title = []
        for h in hemi:
            hemi_data = []
            conn_str = []
            for seed_idx in range(len(roi_idx[h])):
                for target_idx in range(seed_idx+1,len(roi_idx[h])):
                    seed = roi_idx[h][seed_idx]
                    target = roi_idx[h][target_idx]
                    idx = np.intersect1d(np.nonzero(il[0]==seed)[0],np.nonzero(il[1]==target_idx)[0])
                    if len(idx)==0:
                        idx = np.intersect1d(np.nonzero(il[1]==seed)[0],np.nonzero(il[0]==target)[0])
                    hemi_data.append(band_data[idx])
                    this_conn = [k for k,v in areas.iteritems() for i in [seed, target] if roi_vals[i] in v]
                    conn_str.append(this_conn)
            subj_data.append(hemi_data)
            conn_title.append(['%d-%d(%d)'%(i,j,h) for i,j in conn_str])
        if s in g1:
            g1_data[b].append(np.array(subj_data).flatten())
        elif s in g2:
            g2_data[b].append(np.array(subj_data).flatten())
        elif s in g3:
            g3_data[b].append(np.array(subj_data).flatten())
conn_title = [i for j in conn_title for i in j]

scores = 0
for b in bands:
    print '\n\n:::::::::::::', band_names[b], '::::::::::::::'
    g1_band_data = np.array(g1_data[b])
    g2_band_data = np.array(g2_data[b])
    g3_band_data = np.array(g3_data[b])
    print '=== nvVSper ==='
    scores += do_tests(g1_band_data, g2_band_data, copy.deepcopy(conn_title))
    print '=== nvVSrem ==='
    scores += do_tests(g1_band_data, g3_band_data, copy.deepcopy(conn_title))
    print '=== remVSper ==='
    scores += do_tests(g2_band_data, g3_band_data, copy.deepcopy(conn_title))
    # sorted_scores = np.argsort(scores)[::-1]
    # for i in sorted_scores:
    #     if scores[i]>0:
    #         print conn_title[i],':',scores[i]