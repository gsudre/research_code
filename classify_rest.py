# classifies MEG and fMRI subjects in one of the 3 groups (pairwise), and then
# try the classification using the combination of data
import os
import numpy as np
home = os.path.expanduser('~')

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
g1 = 'NV'
g2 = 'persistent'

####
# open fMRI data
####
# load the order of subjects within the data matrix
subjs_fname = home + '/data/fmri/joel_all.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

g1_fmri, g2_fmri = [], []
for seed in seeds:
    g1_seed, g2_seed = [], []
    data_dir = home + '/data/results/fmri_Yeo/seeds/' + seed + '/' 
    print 'Loading fMRI data...' 
    data = np.genfromtxt(data_dir + 'joel_all_corr_downsampled.txt')
    for rec in phen:
        subj_idx = subjs.index('%04d'%rec[0])
        if rec[2] == g1:
            g1_seed.append(data[:,subj_idx])
        elif rec[2] == g2:
            g2_seed.append(data[:,subj_idx]) 
    g1_fmri.append(g1_seed)
    g2_fmri.append(g2_seed)


# # ####
# # # open MEG data
# # ####
# # the idea is the same as when we open the fMRI data, except that now we have 
# # a list inside the lists, for each band
# g1_meg, g2_meg = [], []
# for seed in seeds:
#     g1_seed, g2_seed = [], []
#     data_dir = home + '/data/results/meg_Yeo/seeds/' + seed + '/'
#     for b in bands:
#         g1_band, g2_band = [], []
#         data = np.load(data_dir+'/correlations_%s-%s.npy'%(b[0],b[1]))[()]
#         for rec in phen:
#             if rec[2] == g1:
#                 g1_band.append(data[rec[1]])
#             elif rec[2] == g2:
#                 g2_band.append(data[rec[1]]) 
#         g1_seed.append(g1_band)
#         g2_seed.append(g2_band)
#     g1_meg.append(g1_seed)
#     g2_meg.append(g2_seed)


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
cs = [.1, .25, .5]#, .75, 1]#np.arange(.1,10,.5)
from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.cross_validation import LeaveOneOut, StratifiedShuffleSplit, StratifiedKFold
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import matthews_corrcoef, f1_score, roc_auc_score, recall_score, precision_score, accuracy_score
from sklearn.decomposition import FastICA, PCA, FactorAnalysis

########
# fmri classification
########
nfeats = len(g1_fmri[0][0])
nobs = len(g1_fmri[0])+len(g2_fmri[0]) 
cv = LeaveOneOut(nobs)
inner_cv = LeaveOneOut(nobs-1)
# preds is a list of lists, where the first index is the fold, and inside that 
# list there is one prediction per seed. Same thing for certainty
preds = []
certainty = []
for oidx, (train, test) in enumerate(cv):
    preds.append([])
    certainty.append([])
    # each network has a vote in that cross validation fold
    for s in range(len(seeds)):
        X = np.vstack([np.array(g1_fmri[s]), np.array(g2_fmri[s])])
        y = np.array(labels)
        X = preprocessing.scale(X)

        print 'seed %d: cv %d/%d'%(s+1,oidx+1,nobs)
        X_train = X[train]
        X_test = X[test]
        y_train = y[train]
        y_test = y[test]
        c_val_scores = []
        dimred = FactorAnalysis(n_components=20)
        X_train = dimred.fit_transform(X_train)
        X_test = dimred.transform(X_test)
        for c in cs:
            inner_preds = []
            clf = LogisticRegression(C=c, penalty="l1", dual=False, class_weight='auto')
            for iidx, (itrain, itest) in enumerate(inner_cv):
                X_inner_train = X_train[itrain]
                X_val = X_train[itest]
                y_inner_train = y_train[itrain]
                y_val = y_train[itest]
                scaler = preprocessing.StandardScaler().fit(X_inner_train)
                X_inner_train = scaler.transform(X_inner_train)
                X_val = scaler.transform(X_val)
                clf.fit(X_inner_train, y_inner_train)
                inner_preds.append(clf.predict(X_val))
            c_val_scores.append(f1_score(y_train, inner_preds, pos_label=1))
        best_c = cs[np.argmax(c_val_scores)]
        clf = LogisticRegression(C=best_c, penalty="l1", dual=False, class_weight='auto')
        clf.fit(X_train,y_train)
        print 'Best C=%.2f'%(best_c)
        preds[-1].append(clf.predict(X_test))
        certainty[-1].append(np.max(clf.predict_proba(X_test)))


# ########
# # meg classification
# ########
# nfeats = len(g1_meg[0][0][0])
# nobs = len(g1_meg[0][0])+len(g2_meg[0][0]) 
# cv = LeaveOneOut(nobs)
# inner_cv = LeaveOneOut(nobs-1)
# # preds is a list of lists, where the first index is the fold, and inside that 
# # list there is one prediction per seed with all bands, then another seed and all band.... Same thing for certainty
# preds = []
# certainty = []
# for oidx, (train, test) in enumerate(cv):
#     preds.append([])
#     certainty.append([])
#     # each network has a vote in that cross validation fold
#     for s in range(len(seeds)):
#         for b in range(len(bands)):
#             X = np.vstack([np.array(g1_meg[s][b]), np.array(g2_meg[s][b])])
#             X = np.squeeze(X)
#             imp = preprocessing.Imputer(missing_values='NaN', strategy='mean', axis=0)
#             imp.fit(X)
#             X = imp.transform(X)
#             y = np.array(labels)
#             X = preprocessing.scale(X)

#             print 'seed %d, band %d: cv %d/%d'%(s+1,b+1,oidx+1,nobs)
#             X_train = X[train]
#             X_test = X[test]
#             y_train = y[train]
#             y_test = y[test]
#             c_val_scores = []
#             dimred = FactorAnalysis(n_components=20)
#             X_train = dimred.fit_transform(X_train)
#             X_test = dimred.transform(X_test)
#             for c in cs:
#                 inner_preds = []
#                 clf = LogisticRegression(C=c, penalty="l1", dual=False, class_weight='auto')
#                 for iidx, (itrain, itest) in enumerate(inner_cv):
#                     X_inner_train = X_train[itrain]
#                     X_val = X_train[itest]
#                     y_inner_train = y_train[itrain]
#                     y_val = y_train[itest]
#                     scaler = preprocessing.StandardScaler().fit(X_inner_train)
#                     X_inner_train = scaler.transform(X_inner_train)
#                     X_val = scaler.transform(X_val)
#                     clf.fit(X_inner_train, y_inner_train)
#                     inner_preds.append(clf.predict(X_val))
#                 c_val_scores.append(f1_score(y_train, inner_preds, pos_label=1))
#             best_c = cs[np.argmax(c_val_scores)]
#             clf = LogisticRegression(C=best_c, penalty="l1", dual=False, class_weight='auto')
#             clf.fit(X_train,y_train)
#             print 'Best C=%.2f'%(best_c)
#             preds[-1].append(clf.predict(X_test))
#             certainty[-1].append(np.max(clf.predict_proba(X_test)))
        
# Let's vote on which should be the overall predictions. 
# 1) Round up all votes > thresh. If they diverge, choose the ones with most votes
# 2) If no one has voted with higher than thresh, choose the vote with highest average probability
# Thresh should be established with some type of heuristic. Here, it's as if I'm tossing a coin for as many votes as I have. Therefore, we can use the binomial distribution to get what we want: 1-stats.binom.cdf(.67*len(seeds),len(seeds),.5), which gives about 67%. So, le's play with that:
thresh = .67
final_vote = []
for probs, votes in zip(certainty, preds):
    if max(probs)>thresh:
        good_votes = np.where(np.array(probs)>=thresh)[0]
        avotes = np.array(votes)
        if len(np.unique(avotes[good_votes]))>1:
            # decide by how many seeds voted for each class
            if np.sum(avotes[good_votes]==0) > np.sum(avotes[good_votes]==1):
                final_vote.append(np.array([0]))
            else:
                final_vote.append(np.array([1]))
        else:
            final_vote.append(np.unique(avotes[good_votes]))
    else:
        avotes = np.array(votes)
        aprobs = np.array(probs)
        prob0 = np.mean(aprobs[np.squeeze(avotes==0)])
        prob1 = np.mean(aprobs[np.squeeze(avotes==1)])
        if prob0 > prob1:
            final_vote.append(np.array([0]))
        else:
            final_vote.append(np.array([1]))
acc = np.sum(np.squeeze(final_vote)==y)/float(len(y))
print 'Voting accuracy: ', acc

seed_acc = []
for s in range(len(preds[0])):
    seed_preds = [p[s][0] for p in preds]
    seed_acc.append(accuracy_score(y,seed_preds))
print 'Best seed accuracy: ', max(seed_acc)

# Let's try a different voting scheme. Go with whatever voter was the most certain. IF more than one, use their consensus,
final_vote = []
thresh = .73
for probs, votes in zip(certainty, preds):
    most_certain = max(probs)
    print most_certain
    if np.sum(np.array(probs)==most_certain)>1 or most_certain<thresh:
        good_votes = np.where(np.array(probs)==most_certain)[0]
        avotes = np.array(votes)
        if len(np.unique(avotes[good_votes]))>1:
            print 'disagreement'
            # decide by how many seeds voted for each class
            if np.sum(avotes[good_votes]==0) > np.sum(avotes[good_votes]==1):
                final_vote.append(np.array([0]))
            else:
                final_vote.append(np.array([1]))
        else:
            print 'consensus'
            final_vote.append(np.unique(avotes[good_votes]))
    else:
        print 'best'
        final_vote.append(votes[probs.index(most_certain)])
acc = np.sum(np.squeeze(final_vote)==y)/float(len(y))
print 'Voting accuracy: ', acc
