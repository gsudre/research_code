# classifies MEG and fMRI subjects in one of the 3 groups (pairwise), and then
# try the classification using the combination of data
import os
import numpy as np
home = os.path.expanduser('~')
import sys
sys.path.append(home + '/research_code/PyKCCA-master/')
import kcca, kernels

kernel = kernels.LinearKernel()
phen = np.recfromcsv(home + '/data/overlap_resting/subjs.csv')
bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
# seeds = ['net1_lMidOccipital', 'net2_rParaCentral']
seeds = ['net1_lMidOccipital','net1_lParaHippo','net1_rMidOccipital',
         'net1_rParaHippo','net2_lParaCentral','net2_lPostCentral',
         'net2_lPreCentral','net2_rParaCentral','net2_rPostCentral',
         'net2_rPreCentral','net3_lFusiform','net3_lSuperiorParietal',
         'net3_rFusiform','net3_rSuperiorParietal','net4_lCingulate',
         'net4_lInsula','net4_rCingulate','net4_rInsula','net6_lSupra',
         'net6_rSupra','net7_lACC','net7_lITG','net7_rACC','net7_rITG']
g1 = 'persistent'
g2 = 'remission'

####
# open fMRI data
####
# load the order of subjects within the data matrix
subjs_fname = home + '/data/fmri/joel_all.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

g1_fmri, g2_fmri = [], []
print 'Loading fMRI data...' 
for seed in seeds:
    print seed
    g1_seed, g2_seed = [], []
    data_dir = home + '/data/results/fmri_Yeo/seeds/' + seed + '/' 
    data = np.genfromtxt(data_dir + 'joel_all_corr_downsampled.txt')
    for rec in phen:
        subj_idx = subjs.index('%04d'%rec[0])
        if rec[2] == g1:
            g1_seed.append(data[:,subj_idx])
        elif rec[2] == g2:
            g2_seed.append(data[:,subj_idx]) 
    g1_fmri.append(g1_seed)
    g2_fmri.append(g2_seed)

# ####
# # open MEG data
# ####
# the idea is the same as when we open the fMRI data, except that now we have 
# a list inside the lists, for each band
g1_meg, g2_meg = [], []
print 'Loading MEG data...' 
for seed in seeds:
    print seed
    g1_seed, g2_seed = [], []
    data_dir = home + '/data/results/meg_Yeo/seeds/' + seed + '/'
    for b in bands:
        g1_band, g2_band = [], []
        data = np.load(data_dir+'/correlations_%s-%s.npy'%(b[0],b[1]))[()]
        for rec in phen:
            if rec[2] == g1:
                g1_band.append(data[rec[1]])
            elif rec[2] == g2:
                g2_band.append(data[rec[1]]) 
        g1_seed.append(g1_band)
        g2_seed.append(g2_band)
    g1_meg.append(g1_seed)
    g2_meg.append(g2_seed)

####
# constructing labels (same for fMRI and MEG)
####
labels = []
for rec in phen:
    if rec[2] == g1:
        labels.append(0)
    elif rec[2] == g2:
        labels.append(1) 

########
# Starting cross-validation loops
######## 
cs = [.1, .25, .5, .75, 1]
ncomps = [2,5,10,20]
regs = [1e-5, 1e-6, 1e-4, 1e-3]
cs = [.1]
ncomps = [2]
regs = [1e-5]
params = [[i,j,k] for i in cs for j in ncomps for k in regs]
from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.cross_validation import LeaveOneOut, StratifiedShuffleSplit, StratifiedKFold
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import matthews_corrcoef, f1_score, recall_score, precision_score, accuracy_score
from sklearn.decomposition import FastICA, PCA, FactorAnalysis


########
# kCCA and classification
########
nfeats = len(g1_meg[0][0][0])
nobs = len(g1_fmri[0])+len(g2_fmri[0]) 
cv = LeaveOneOut(nobs)
inner_cv = LeaveOneOut(nobs-1)
# preds is a list of lists, where the first index is the seed, and inside that 
# list there is one prediction per fold. Same thing for certainty
fmri_preds = []
fmri_certainty = []
meg_preds = []
meg_certainty = []
for s in range(len(seeds)):
    fmri_preds.append([])
    fmri_certainty.append([])
    meg_preds.append([])
    meg_certainty.append([])

    # grab the fMRI data, which is not band-dependent
    X_fmri = np.vstack([np.array(g1_fmri[s]), np.array(g2_fmri[s])])
    # for MEG we'll concatenate the data for all bands
    X_meg = []
    for b in range(len(bands)):
        X = np.vstack([np.array(g1_meg[s][b]), np.array(g2_meg[s][b])])
        X = np.squeeze(X)
        imp = preprocessing.Imputer(missing_values='NaN', strategy='mean', axis=0)
        imp.fit(X)
        X = imp.transform(X)
        X_meg.append(X)
    X_meg = np.array(X_meg).swapaxes(1,0).reshape([nobs,-1])

    X_fmri = preprocessing.scale(X_fmri)
    X_meg = preprocessing.scale(X_meg)
    y = np.array(labels)

    # each network has a vote in that cross validation fold
    for oidx, (train, test) in enumerate(cv):
        print 'seed %d: cv %d/%d'%(s+1,oidx+1,nobs)
        
        X_fmri_train = X_fmri[train]
        X_fmri_test = X_fmri[test]
        X_meg_train = X_meg[train]
        X_meg_test = X_meg[test]
        y_train = y[train]
        y_test = y[test]
        fmri_val_scores = []
        meg_val_scores = []
        for c, ncomp, reg in params:
            fmri_inner_preds = []
            meg_inner_preds = []

            cca = kcca.KCCA(kernel, kernel, regularization=reg, decomp='full',
                        method='kettering_method', scaler1=lambda x:x, 
                        scaler2=lambda x:x)
            clf = LogisticRegression(C=c, penalty="l1", dual=False, class_weight='auto')
            for iidx, (itrain, itest) in enumerate(inner_cv):
                X_meg_inner_train = X_meg_train[itrain]
                X_meg_val = X_meg_train[itest]
                X_fmri_inner_train = X_fmri_train[itrain]
                X_fmri_val = X_fmri_train[itest]
                y_inner_train = y_train[itrain]
                y_val = y_train[itest]

                cca = cca.fit(X_fmri_inner_train,X_meg_inner_train)
                fmri_train, meg_train = cca.transform(X_fmri_inner_train, 
                                                      X_meg_inner_train)
                fmri_val, meg_val = cca.transform(X_fmri_val, X_meg_val)
                clf.fit(fmri_train[:, :ncomp], y_inner_train)
                fmri_inner_preds.append(clf.predict(X_fmri_val[:, :ncomp]))
                clf.fit(meg_train[:, :ncomp], y_inner_train)
                meg_inner_preds.append(clf.predict(X_meg_val[:, :ncomp]))
            fmri_val_scores.append(accuracy_score(y_train, fmri_inner_preds))
            meg_val_scores.append(accuracy_score(y_train, meg_inner_preds))
        avg_scores = (np.array(fmri_val_scores)+np.array(meg_val_scores))/2
        c, ncomp, reg = params[np.argmax(avg_scores)]
        print 'Best fold: C=%.2f, comp=%d, reg=%f'%(c,ncomp,reg)

        clf = LogisticRegression(C=c, penalty="l1", dual=False, class_weight='auto')
        cca = kcca.KCCA(kernel, kernel, regularization=reg, decomp='full',
                        method='kettering_method', scaler1=lambda x:x, 
                        scaler2=lambda x:x)
        cca = cca.fit(X_fmri_train,X_meg_train)
        fmri_train, meg_train = cca.transform(X_fmri_train, X_meg_train)
        fmri_test, meg_test = cca.transform(X_fmri_test, X_meg_test)
        
        clf.fit(fmri_train[:, :ncomp], y_train)
        fmri_preds[-1].append(clf.predict(fmri_test[:, :ncomp]))
        fmri_certainty[-1].append(np.max(clf.predict_proba(fmri_test[:, :ncomp])))
        
        clf.fit(meg_train[:, :ncomp], y_train)
        meg_preds[-1].append(clf.predict(meg_test[:, :ncomp]))
        meg_certainty[-1].append(np.max(clf.predict_proba(meg_test[:, :ncomp])))
    print 'Seed %s: fmri=%.2f, meg=%.2f'%(seeds[s], 
                                          accuracy_score(np.squeeze(fmri_preds[-1]),y),
                                          accuracy_score(np.squeeze(meg_preds[-1]),y))
        
        
        
        
# # Let's vote on which should be the overall predictions. 
# # 1) Round up all votes > thresh. If they diverge, choose the ones with most votes
# # 2) If no one has voted with higher than thresh, choose the vote with highest average probability
# # Thresh should be established with some type of heuristic. Here, it's as if I'm tossing a coin for as many votes as I have. Therefore, we can use the binomial distribution to get what we want: 1-stats.binom.cdf(.67*len(seeds),len(seeds),.5), which gives about 67%. So, le's play with that:
# thresh = .67
# final_vote = []
# for probs, votes in zip(certainty, preds):
#     if max(probs)>thresh:
#         good_votes = np.where(np.array(probs)>=thresh)[0]
#         avotes = np.array(votes)
#         if len(np.unique(avotes[good_votes]))>1:
#             # decide by how many seeds voted for each class
#             if np.sum(avotes[good_votes]==0) > np.sum(avotes[good_votes]==1):
#                 final_vote.append(np.array([0]))
#             else:
#                 final_vote.append(np.array([1]))
#         else:
#             final_vote.append(np.unique(avotes[good_votes]))
#     else:
#         avotes = np.array(votes)
#         aprobs = np.array(probs)
#         prob0 = np.mean(aprobs[np.squeeze(avotes==0)])
#         prob1 = np.mean(aprobs[np.squeeze(avotes==1)])
#         if prob0 > prob1:
#             final_vote.append(np.array([0]))
#         else:
#             final_vote.append(np.array([1]))
# acc = np.sum(np.squeeze(final_vote)==y)/float(len(y))
# print 'Voting accuracy: ', acc

# seed_acc = []
# for s in range(len(preds[0])):
#     seed_preds = [p[s][0] for p in preds]
#     seed_acc.append(accuracy_score(y,seed_preds))
# print 'Best seed accuracy: ', max(seed_acc)

# # Let's try a different voting scheme. Go with whatever voter was the most certain. IF more than one, use their consensus,
# final_vote = []
# thresh = .73
# for probs, votes in zip(certainty, preds):
#     most_certain = max(probs)
#     print most_certain
#     if np.sum(np.array(probs)==most_certain)>1 or most_certain<thresh:
#         good_votes = np.where(np.array(probs)==most_certain)[0]
#         avotes = np.array(votes)
#         if len(np.unique(avotes[good_votes]))>1:
#             print 'disagreement'
#             # decide by how many seeds voted for each class
#             if np.sum(avotes[good_votes]==0) > np.sum(avotes[good_votes]==1):
#                 final_vote.append(np.array([0]))
#             else:
#                 final_vote.append(np.array([1]))
#         else:
#             print 'consensus'
#             final_vote.append(np.unique(avotes[good_votes]))
#     else:
#         print 'best'
#         final_vote.append(votes[probs.index(most_certain)])
# acc = np.sum(np.squeeze(final_vote)==y)/float(len(y))
# print 'Voting accuracy: ', acc
