# Makes a matrix of subjects x correlations, where the correlations are seed to seed
import numpy as np
import os
import csv
home = os.path.expanduser('~')

s_fname = home+'/data/fmri_solar/seeds_MNI_LPI.txt'
sn_fname = home+'/data/fmri_solar/seeds_names.txt'
sc_fname = home+'/data/fmri_solar/seed_correlations.txt'
subjs_fname = home+'/data/fmri_solar/subjs_aligned_clean.txt'
out_fname = home+'/data/fmri_solar/seed2seed_correlations.csv'
tmp_dir = home + '/tmp/'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

fid = open(s_fname, 'r')
seeds = [line.rstrip() for line in fid]
fid.close()

fid = open(sn_fname, 'r')
seed_names = [line.rstrip() for line in fid]
fid.close()

if len(seeds)!=len(seed_names):
    raise('ERROR: Number of seed names needs to match number of seeds!')

seed_corrs = np.recfromcsv(sc_fname)

# for each subject
all_corrs = []
for subj in subjs:
    # create a time series for each seed
    for seed, name in zip(seeds, seed_names):
        mydir='/mnt/neuro/data_by_maskID/%s/afni/%s.rest.compCor.results'%(subj,subj)
        cmd_line = '3dmaskave -q -nball %s 5 %s/errts.%s.compCor+tlrc > %s/seed_%s.1D'%(seed,mydir,subj,tmp_dir,name)
        os.system(cmd_line)
    # computing all correlations
    subj_corrs = []
    for sc in seed_corrs:
        seed1 = np.genfromtxt('%s/seed_%s.1D'%(tmp_dir,sc[0]))
        seed2 = np.genfromtxt('%s/seed_%s.1D'%(tmp_dir,sc[1]))
        # if there were problems creating the seed average
        if len(seed1)==0 or len(seed2)==0:
            subj_corrs.append(np.nan)
        else:
            val = np.corrcoef(seed1,seed2)[0,1]
            subj_corrs.append(val)
    all_corrs.append(subj_corrs)

# # scale data
# tmp = np.array(all_corrs)
# # cannot use zscores because of nans
# scaled = (tmp-np.nanmean(tmp,axis=0))/np.nanstd(tmp,axis=0)
# scaled_l = [list(s) for s in scaled]
all_data = all_corrs

# construct header and first column
header = ['maskids']
for sc in seed_corrs:
    header.append('%s_%s'%(sc[0],sc[1]))

rows = [[i] + k for i,k in zip(subjs, all_data)]
rows.insert(0,header)

fout = open(out_fname, 'w')
wr = csv.writer(fout)
wr.writerows(rows)
fout.close()
