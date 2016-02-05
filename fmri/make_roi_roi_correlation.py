# Makes a matrix of subjects x correlations, where the correlations are roi to roi
import numpy as np
import os
import csv
import itertools
home = os.path.expanduser('~')

age = 'kids'
rois_fname = home+'/data/fmri_solar/rois_philip.txt'
subjs_fname = home+'/data/fmri_solar/subjs_%s_aligned_clean.txt'%age
mask_dir = home+'/data/fmri_solar/roi_masks/'
out_fname = home+'/data/fmri_solar/roi2roi_philip_%s.csv'%age
tmp_dir = home + '/tmp/%s/'%age

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

fid = open(rois_fname, 'r')
roi_corrs = [line.rstrip().split(',') for line in fid]
fid.close()

# for each subject
all_corrs = []
for subj in subjs:
    # create a time series for each roi
    for rois in roi_corrs:
        for roi in rois:
            myfile = '/mnt/neuro/data_by_maskID/%s/afni/%s.rest.compCor.results/errts.%s.compCor+tlrc'%(subj,subj,subj)
            if age=='adults':
                mask = mask_dir + '/%s+tlrc'%roi
            else:
                mask = mask_dir + '/k_%s+tlrc'%roi
            # for some weird reason, a few mask ids have the wrong errts dimensions. So, we'll need to create one mask per subject
            cmd_line = '3dresample -overwrite -master %s -inset %s -prefix %s/tmp_mask+tlrc'%(myfile, mask, tmp_dir)
            os.system(cmd_line)
            cmd_line = '3dmaskave -quiet -mask %s/tmp_mask+tlrc %s > %s/%s.1D'%(tmp_dir,myfile,tmp_dir,roi)
            os.system(cmd_line)
    # at this point we have one average time series for each ROI in the list. 
    subj_corrs = []
    for rc in roi_corrs:
        # calculate the pairwise correlations within the selection
        for pair_comb in itertools.combinations(rc,2):
            seed1 = np.genfromtxt('%s/%s.1D'%(tmp_dir,pair_comb[0]))
            seed2 = np.genfromtxt('%s/%s.1D'%(tmp_dir,pair_comb[1]))
            # if there were problems creating the seed average
            if len(seed1)==0 or len(seed2)==0:
                val = np.nan
            else:
                val = np.corrcoef(seed1,seed2)[0,1]
            subj_corrs.append(val) 
    all_corrs.append(subj_corrs)

# construct header and first column
header = ['maskids']
for rc in roi_corrs:
    for rcomb in itertools.combinations(rc,2):
        header.append('_'.join(rcomb))

rows = [[i] + k for i,k in zip(subjs, all_corrs)]
rows.insert(0,header)

fout = open(out_fname, 'w')
wr = csv.writer(fout)
wr.writerows(rows)
fout.close()
