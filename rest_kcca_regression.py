# classifies MEG and fMRI subjects in one of the 3 groups (pairwise), and then
# try the classification using the combination of data
import os
import numpy as np
home = os.path.expanduser('~')
import sys
sys.path.append(home + '/research_code/PyKCCA-master/')
import kcca, kernels
from sklearn import preprocessing
from scipy import stats

kernel = kernels.LinearKernel()
phen = np.recfromcsv(home + '/data/overlap_resting/subjs.csv')
out_dir = home + '/data/results/overlap_resting/tmp/'
if len(sys.argv)>10:
    seed, band = sys.argv[1:]
else:
    seed = 'net6_rSupra'
    band = [65,100]

####
# open fMRI data
####
# load the order of subjects within the data matrix
subjs_fname = home + '/data/fmri/joel_all.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

X_fmri,inatt,hi = [],[],[]
print 'Loading fMRI data...' 
data_dir = home + '/data/results/fmri_Yeo/seeds/' + seed + '/' 
data = np.genfromtxt(data_dir + 'joel_all_corr_downsampled.txt')
data = data[:,6:]  # removes x,y,z and i,j,k
for rec in phen:
    subj_idx = subjs.index('%04d'%rec[0])
    if rec['dx'] in ['persistent','remission']:
        X_fmri.append(data[:,subj_idx])
        hi.append(rec['hi'])
        inatt.append(rec['inatt'])
X_fmri = np.array(X_fmri)
inatt = np.array(inatt)
hi = np.array(hi)

# ####
# # open MEG data
# ####
# the idea is the same as when we open the fMRI data, except that now we have 
# a list inside the lists, for each band
X_meg = []
print 'Loading MEG data...' 
data_dir = home + '/data/results/meg_Yeo/seeds/' + seed + '/'
data = np.load(data_dir+'/correlations_%s-%s.npy'%(band[0],band[1]))[()]
for rec in phen:
    if rec['dx'] in ['persistent','remission']:
        X_meg.append(data[rec[1]]) 
X_meg = np.array(X_meg).squeeze()

# MEG has some subjects if NaNs. If there's a subject only with NaNs, remove it from both datasets
idx = np.isnan(X_meg).all(axis=1)
if np.sum(idx)>0:
    print 'Removing %d subjects'%np.sum(idx)
    X_meg = X_meg[~idx,:]
    X_fmri = X_fmri[~idx,:]
    inatt = inatt[~idx]
    hi = hi[~idx]

# remove features that have NaNs, but keep track of them for the future
idx = np.isnan(X_meg).any(axis=0) # mask of features with at least 1 NaN
X_meg = X_meg[:,~idx]
print 'MEG Features left: %d/%d'%(X_meg.shape[1],len(idx))

X_fmri = preprocessing.scale(X_fmri)
X_meg = preprocessing.scale(X_meg)

cca = kcca.KCCA(kernel, kernel,decomp='full', regularization=1e-5,
                method='kettering_method', scaler1=lambda x:x, 
                scaler2=lambda x:x)
cca = cca.fit(X_fmri,X_meg)
X_fmri2, X_meg2 = cca.transform(X_fmri, X_meg)

fmri_rs, fmri_pvals = [],[]
meg_rs, meg_pvals = [],[]
y = inatt
for f in range(X_meg2.shape[1]):
    r, p = stats.pearsonr(X_fmri2[:,f], y)
    fmri_rs.append(r)
    fmri_pvals.append(p)

    r, p = stats.pearsonr(X_meg2[:,f], y)
    meg_rs.append(r)
    meg_pvals.append(p)