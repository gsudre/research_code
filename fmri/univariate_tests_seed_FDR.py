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

g1_fname = home + '/data/fmri/joel_nvs.txt'
g2_fname = home + '/data/fmri/joel_persistent.txt'
g3_fname = home + '/data/fmri/joel_remission.txt'
subjs_fname = home + '/data/fmri/joel_all.txt'
inatt_fname = home + '/data/fmri/inatt.txt'
hi_fname = home + '/data/fmri/hi.txt'
if len(sys.argv)>1:
    data_dir = home + '/data/results/fmri_Yeo/seeds/%s/'%sys.argv[1]
    my_test = sys.argv[2]
# data_dir = home + '/data/results/fmri_Yeo/seeds/net1_lMidOccipital/'
# my_test = 'useAll'

thresh = .05
alphas = [.1, .05, .01]

fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid3 = open(g3_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
g3 = [line.rstrip() for line in fid3]
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
res = np.recfromtxt(inatt_fname, delimiter='\t')
inatt = {}
for rec in res:
    inatt[rec[0]] = rec[1]
res = np.recfromtxt(hi_fname, delimiter='\t')
hi = {}
for rec in res:
    hi[rec[0]] = rec[1]

g1_data = []
g2_data = []
g3_data = []
g1_subjs=[]
g2_subjs=[]
g3_subjs=[]
g2_inatt = []
g2_hi = []
g3_inatt = []
g3_hi = []

print 'Loading data...'
data = np.genfromtxt(data_dir + '/joel_all_corr_downsampled.txt')
print data_dir
print my_test

data = data[:,6:]
cnt=0
for s in subjs:
    if s in g1:
        g1_data.append(data[:,cnt].T)
        g1_subjs.append(s)
    elif s in g2:
        g2_data.append(data[:,cnt].T)
        g2_subjs.append(s)
        g2_inatt.append(inatt[int(s)])
        g2_hi.append(hi[int(s)])
    elif s in g3:
        g3_data.append(data[:,cnt].T)
        g3_subjs.append(s)
        g3_inatt.append(inatt[int(s)])
        g3_hi.append(hi[int(s)])
    cnt+=1

inatt = g2_inatt + g3_inatt
hi = g2_hi + g3_hi
all_ps = []
all_clusters = []

X = np.arctanh(np.array(g1_data))
Y = np.arctanh(np.array(g2_data))
Z = np.arctanh(np.array(g3_data))

# tail=1 because we use 1-pvalue as threshold for correlations
if my_test=='inatt':
    sx = np.array(inatt)
    brain = np.vstack([Y,Z])
elif my_test=='hi':
    sx = np.array(hi)
    brain = np.vstack([Y,Z])
elif my_test=='nvVSper':
    brain1 = X
    brain2 = Y
elif my_test=='nvVSrem':
    brain1 = X
    brain2 = Z
elif my_test=='perVSrem':
    brain1 = Y
    brain2 = Z
elif my_test=='nvVSadhd':
    brain1 = X
    brain2 = np.vstack([Y,Z])
elif my_test=='onlyNV':
    alphas = [1e-11]
    brain = X
elif my_test=='useAll':
    alphas = [1e-11]
    brain = np.vstack([X,Y,Z])

if my_test.find('i')>=0:
    pvals = []
    nfeats = brain.shape[1]
    nsubjs = brain.shape[0]
    for i in range(nfeats):
        vec = brain[:,i]
        keep = ~np.isnan(vec)
        # 2-tailed p-value by default
        pvals.append(stats.pearsonr(sx[keep], vec[keep])[1])
    pvals = np.array(pvals)
elif my_test.find('VS')>=0:
    nsubjs = brain1.shape[0] + brain2.shape[0]
    pvals = stats.ttest_ind(brain1,brain2,axis=0,equal_var=True)[1]
else:
    nsubjs = brain.shape[0]
    pvals = stats.ttest_1samp(brain,popmean=0,axis=0)[1]
  
idx = ~np.isnan(pvals)
for a in alphas:
    reject_fdr, pval_fdr = mne.stats.fdr_correction(pvals[idx], alpha=a, method='indep')
    num_good = np.sum(reject_fdr)
    if num_good > 0:
        print '\n\nGood voxels at %.1e: %d\n\n'%(a,num_good)
        # if we have any good voxels left, put them in their original positions
        tvals = -stats.distributions.t.ppf(pvals/2, nsubjs-1)
        tvals[~reject_fdr] = 0
        tvals[~idx] = 0
        # make .nii with p-values
        fname = data_dir+my_test+'_FDR_a%.2ft%.2f'%(a,thresh)
        write2afni(tvals,fname,resample=True)
