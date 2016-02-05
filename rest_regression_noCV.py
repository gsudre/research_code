# Data fusion between MEG and fMRI, no CV, and write out the correlation of each component to inattention symptoms
import os
import numpy as np
home = os.path.expanduser('~')
import csv
from sklearn import preprocessing
from scipy import stats

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
seeds = ['net1_lMidOccipital','net1_lParaHippo','net1_rMidOccipital','net1_rParaHippo','net2_lParaCentral','net2_lPostCentral', 'net2_lPreCentral','net2_rParaCentral','net2_rPostCentral','net2_rPreCentral','net3_lFusiform','net3_lSuperiorParietal','net2_rParaCentral','net2_rPostCentral','net2_rPreCentral','net3_lFusiform','net3_lSuperiorParietal','net3_rFusiform','net3_rSuperiorParietal','net4_lCingulate','net4_lInsula','net4_rCingulate','net4_rInsula','net6_lSupra','net6_rSupra','net7_lACC','net7_lITG','net7_rACC','net7_rITG']

phen = np.recfromcsv(home + '/data/overlap_resting/subjs.csv')
out_fname = home + '/tmp/whole_pls.csv'


####
# open fMRI data
####
# load the order of subjects within the data matrix
subjs_fname = home + '/data/fmri/joel_all.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

all_results = []
for seed in seeds:
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
    X_fmri0 = np.array(X_fmri)
    inatt0 = np.array(inatt)
    hi0 = np.array(hi)

    for band in bands:
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
            X_fmri = X_fmri0[~idx,:]
            inatt = inatt0[~idx]
            hi = hi0[~idx]

        # remove features that have NaNs, but keep track of them for the future
        idx = np.isnan(X_meg).any(axis=0) # mask of features with at least 1 NaN
        X_meg = X_meg[:,~idx]
        print 'MEG Features left: %d/%d'%(X_meg.shape[1],len(idx))

        X_fmri = preprocessing.scale(X_fmri)
        X_meg = preprocessing.scale(X_meg)
        y = inatt

        from sklearn.pls import PLSCanonical

        ncomps = 10
        plsca = PLSCanonical(n_components=ncomps)
        plsca.fit(X_meg, X_fmri)
        X_mc, X_fc = plsca.transform(X_meg, X_fmri)

        res = []
        print seed, band
        for comp in range(ncomps):
            r,p = stats.pearsonr(X_mc[:,comp], y)
            res += [r,p]
            r,p = stats.pearsonr(X_fc[:,comp], y)
            res += [r,p]
        all_results.append(['%s_%d-%d'%(seed,band[0],band[1])] + res)
header = []
for d in range(ncomps):
    header+=['meg r%d'%d, 'meg_p%d'%d, 'fmri r%d'%d, 'fmri_p%d'%d]
header = ['data'] + header
all_results.insert(0, header)

fout = open(out_fname, 'w')
wr = csv.writer(fout)
wr.writerows(all_results)
fout.close()