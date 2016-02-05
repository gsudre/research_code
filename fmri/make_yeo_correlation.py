# Makes a matrix of subjects x correlations, where the correlations are roi to roi using the Yeo network intersections
import numpy as np
import os
import csv
import itertools
import copy
home = os.path.expanduser('~')

age = 'kids'
data_dir = home + '/data/slim_yeo/'
subjs_fname = home+'/data/fmri_solar/subjs_%s_aligned_clean.txt'%age
out_fname = home+'/data/fmri_solar/roi2roi_slimyeo_%s.csv'%age
nets = [1,2,3,4,5,6,7]

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

# for each subject
all_corrs = []
for subj in subjs:
    subj_corrs = []
    for net in nets:
        # figure out all ROIs for which to compute correlation
        if age=='adults':
            rois_fname = data_dir + '/regionsIn%d.1D'%net #'/regionsIn%d_10pct_clean.1D'%net
        else:
            rois_fname = data_dir + '/regionsIn%d.1D'%net #'/k_regionsIn%d_10pct_clean.1D'%net
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

# # construct header (only for adults)
# if age=='adults':
#     header = ['maskids']
#     for net in nets:
#         rois_fname = data_dir + '/regionsIn%d_10pct_clean.1D'%net
#         fid = open(rois_fname, 'r')
#         rois = [line.rstrip() for line in fid]
#         fid.close()
#         # find the name of each region
#         names_fname = data_dir + '/desai_atlas_code.txt'
#         fid = open(names_fname, 'r')
#         roi_names = copy.deepcopy(rois)
#         for line in fid:
#             i = 0
#             found = False
#             while i<len(roi_names) and not found:
#                 if line.rstrip().split(':')[-1]==rois[i]:
#                     found = True
#                     roi_names[i] = line.rstrip().split(':')[-2].replace('ctx-','')
#                 i += 1
#         for rcomb in itertools.combinations(roi_names,2):
#             header.append('_'.join(rcomb))
#     rows.insert(0,header)

# construct header (only for adults), slim version
if age=='adults':
    header = ['maskids']
    for net in nets:
        rois_fname = data_dir + '/regionsIn%d.1D'%net
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
