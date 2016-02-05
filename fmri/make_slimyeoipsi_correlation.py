# Makes a matrix of subjects x correlations, where the correlations are roi to roi using the Yeo network non-continuous maps. This is just for ipsilateral
# only connections.
import numpy as np
import os
import csv
import itertools
home = os.path.expanduser('~')

age = 'kids'
data_dir = home + '/data/slim_yeo/'
subjs_fname = home+'/data/fmri_solar/subjs_%s_aligned_clean.txt'%age
out_fname = home+'/data/fmri_solar/roi2roi_slimyeoipsi_%s.csv'%age
nets = [3,4,6,7]

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

# for each subject
all_corrs = []
for subj in subjs:
    subj_corrs = []
    for net in nets:
        for hemi in ['L', 'R']:
            # figure out all ROIs for which to compute correlation
            if age=='adults':
                rois_fname = data_dir + '/regionsIn%d_%s.1D'%(net,hemi)
            else:
                rois_fname = data_dir + '/regionsIn%d_%s.1D'%(net,hemi)
            fid = open(rois_fname, 'r')
            rois = [line.rstrip() for line in fid]
            fid.close()

            # calculate the pairwise correlations within the network
            net_dir = data_dir + '/net%d/'%net
            for rcomb in itertools.combinations(rois,2):
                seed1 = np.genfromtxt('%s/%s_%sin%d.1D'%(net_dir,subj,rcomb[0],net))
                seed2 = np.genfromtxt('%s/%s_%sin%d.1D'%(net_dir,subj,rcomb[1],net))
                # if there were problems creating the seed average
                if len(seed1)==0 or len(seed2)==0:
                    val = np.nan
                else:
                    val = np.corrcoef(seed1,seed2)[0,1]
                subj_corrs.append(val) 
    all_corrs.append(subj_corrs)

# construct first column
rows = [[i] + k for i,k in zip(subjs, all_corrs)]

# construct header (only for adults), slim version
if age=='adults':
    header = ['maskids']
    for hemi in ['L', 'R']:
        for net in nets:
            rois_fname = data_dir + '/regionsIn%d_%s.1D'%(net,hemi)
            fid = open(rois_fname, 'r')
            rois = [line.rstrip() for line in fid]
            fid.close()
            for rcomb in itertools.combinations(rois,2):
                header.append('net%d_'%net + '_'.join(rcomb))
    rows.insert(0,header)

fout = open(out_fname, 'w')
wr = csv.writer(fout)
wr.writerows(rows)
fout.close()
