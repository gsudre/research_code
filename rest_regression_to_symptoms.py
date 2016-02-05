# Data fusion with specific symptom counts as targets
import os
import numpy as np
home = os.path.expanduser('~')
import sys
from sklearn import preprocessing

phen = np.recfromcsv(home + '/data/overlap_resting/subjs.csv')
out_dir = home + '/data/results/overlap_resting/tmp/'
if len(sys.argv)>1:
    seed, band = sys.argv[1:]
    band = band.split('-')
else:
    seed = 'net2_lPrecentral'
    band = [1,4]

within=True
print seed
print band

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
    if rec['dx'] in ['NV','persistent','remission']:
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
    if rec['dx'] in ['NV','persistent','remission']:
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

from sklearn.cross_validation import ShuffleSplit
from sklearn.pls import PLSRegression
from sklearn.metrics import mean_absolute_error
from sklearn.dummy import DummyRegressor

nobs = X_meg.shape[0]
max_comps = range(5,30,5)
nfolds=50
cv = ShuffleSplit(nobs,n_iter=nfolds,test_size=.1)
y = inatt

# Trying the prediction with different components
comp_scores = []
dumb_scores = []
meg_scores, fmri_scores = [], []
for ncomp in max_comps:
    print 'Trying %d components'%ncomp
    pls = PLSRegression(n_components=ncomp)
    dumb = DummyRegressor(strategy='mean')

    mae = 0
    dumb_mae = 0
    meg_mae, fmri_mae = 0, 0
    for oidx, (train, test) in enumerate(cv):
        X_fmri_train = X_fmri[train]
        X_fmri_test = X_fmri[test]
        X_meg_train = X_meg[train]
        X_meg_test = X_meg[test]
        y_train = y[train]
        y_test = y[test]

        X_train = np.hstack([X_fmri_train,X_meg_train])
        X_test = np.hstack([X_fmri_test,X_meg_test])
        
        pls.fit(X_train, y_train)
        pred = pls.predict(X_test)

        mae += mean_absolute_error(y_test, pred)

        dumb.fit(X_train, y_train)
        dumb_pred = dumb.predict(X_test)
        dumb_mae += mean_absolute_error(y_test,dumb_pred)

        if within:
            pls.fit(X_fmri_train, y_train)
            pred = pls.predict(X_fmri_test)
            fmri_mae += mean_absolute_error(y_test, pred)

            pls.fit(X_meg_train, y_train)
            pred = pls.predict(X_meg_test)
            meg_mae += mean_absolute_error(y_test, pred)

    comp_scores.append(mae/nfolds)
    dumb_scores.append(dumb_mae/nfolds)
    fmri_scores.append(fmri_mae/nfolds)
    meg_scores.append(meg_mae/nfolds)

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
if within:
    plt.plot(max_comps,np.array([comp_scores,dumb_scores,fmri_scores,meg_scores]).T)
    plt.legend(['both','dumb','fmri','meg'])
else:
    plt.plot(max_comps,comp_scores,max_comps,dumb_scores)
t_str = seed + str(band)
plt.title(t_str)
plt.savefig(home+'/tmp/inattWithNVsDumbMean_%s_%s.png'%(seed,band[0]))
