# collects the classification results for MEG and fMRI
import os
import numpy as np
home = os.path.expanduser('~')
import sys
sys.path.append(home + '/research_code/PyKCCA-master/')
import glob
from sklearn.metrics import accuracy_score

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
res_dir = home + '/data/results/overlap_resting/'
g1 = 'NV'
g2 = 'persistent'

files = glob.glob(res_dir + '/*_fmri_meg_4-8_%sVS%s.npz'%(g1,g2))
for fname in files:
    res = np.load(fname)
    seed_name = fname.split('/')[-1].split('_')[:2]
    fmri_acc = accuracy_score(res['y'],res['fmri_preds'])
    meg_acc = accuracy_score(res['y'],res['meg_preds'])
    print seed_name, fmri_acc, meg_acc
print '\nTotal %d files.'%len(files)

# ####
# # open fMRI data
# ####
# # load the order of subjects within the data matrix
# subjs_fname = home + '/data/fmri/joel_all.txt'
# fid = open(subjs_fname, 'r')
# subjs = [line.rstrip() for line in fid]
# fid.close()

# g1_fmri, g2_fmri = [], []
# print 'Loading fMRI data...' 
# data_dir = home + '/data/results/fmri_Yeo/seeds/' + seed + '/' 
# data = np.genfromtxt(data_dir + 'joel_all_corr_downsampled.txt')
# for rec in phen:
#     subj_idx = subjs.index('%04d'%rec[0])
#     if rec[2] == g1:
#         g1_fmri.append(data[:,subj_idx])
#     elif rec[2] == g2:
#         g2_fmri.append(data[:,subj_idx]) 

# # ####
# # # open MEG data
# # ####
# # the idea is the same as when we open the fMRI data, except that now we have 
# # a list inside the lists, for each band
# g1_meg, g2_meg = [], []
# print 'Loading MEG data...' 
# data_dir = home + '/data/results/meg_Yeo/seeds/' + seed + '/'
# for b in bands:
#     g1_band, g2_band = [], []
#     data = np.load(data_dir+'/correlations_%s-%s.npy'%(b[0],b[1]))[()]
#     for rec in phen:
#         if rec[2] == g1:
#             g1_band.append(data[rec[1]])
#         elif rec[2] == g2:
#             g2_band.append(data[rec[1]]) 
#     g1_meg.append(g1_band)
#     g2_meg.append(g2_band)

# ####
# # constructing labels (same for fMRI and MEG)
# ####
# labels = []
# for rec in phen:
#     if rec[2] == g1:
#         labels.append(0)
#     elif rec[2] == g2:
#         labels.append(1) 

# ########
# # Starting cross-validation loops
# ######## 
# cs = [.1, .25, .5, .75, 1]
# ncomps = [2,5,10,20]
# regs = [1e-5, 1e-6, 1e-4, 1e-3]
# # cs = [.1]
# # ncomps = [2]
# # regs = [1e-5]
# params = [[i,j,k] for i in cs for j in ncomps for k in regs]
# best_params = []
# from sklearn import preprocessing
# from sklearn.linear_model import LogisticRegression
# from sklearn.svm import SVC
# from sklearn.cross_validation import LeaveOneOut, StratifiedShuffleSplit, StratifiedKFold
# from sklearn.grid_search import GridSearchCV

# from sklearn.decomposition import FastICA, PCA, FactorAnalysis


# ########
# # kCCA and classification
# ########
# nfeats = len(g1_fmri[0])
# nobs = len(g1_fmri)+len(g2_fmri) 
# cv = LeaveOneOut(nobs)
# inner_cv = LeaveOneOut(nobs-1)
# # preds is a list of lists, where the first index is the seed, and inside that 
# # list there is one prediction per fold. Same thing for certainty
# fmri_preds = []
# fmri_certainty = []
# meg_preds = []
# meg_certainty = []

# # grab the fMRI data, which is not band-dependent
# X_fmri = np.vstack([np.array(g1_fmri), np.array(g2_fmri)])
# # for MEG we'll concatenate the data for all bands
# X_meg = []
# for b in range(len(bands)):
#     X = np.vstack([np.array(g1_meg[b]), np.array(g2_meg[b])])
#     X = np.squeeze(X)
#     imp = preprocessing.Imputer(missing_values='NaN', strategy='mean', axis=0)
#     imp.fit(X)
#     X = imp.transform(X)
#     X_meg.append(X)
# X_meg = np.array(X_meg).swapaxes(1,0)
# X_meg = X_meg.reshape([X_meg.shape[0],-1])

# X_fmri = preprocessing.scale(X_fmri)
# X_meg = preprocessing.scale(X_meg)
# y = np.array(labels)

# # each network has a vote in that cross validation fold
# for oidx, (train, test) in enumerate(cv):
#     print 'cv %d/%d'%(oidx+1,nobs)
    
#     X_fmri_train = X_fmri[train]
#     X_fmri_test = X_fmri[test]
#     X_meg_train = X_meg[train]
#     X_meg_test = X_meg[test]
#     y_train = y[train]
#     y_test = y[test]
#     fmri_val_scores = []
#     meg_val_scores = []
#     for c, ncomp, reg in params:
#         fmri_inner_preds = []
#         meg_inner_preds = []

#         cca = kcca.KCCA(kernel, kernel, regularization=reg, decomp='full',
#                     method='kettering_method', scaler1=lambda x:x, 
#                     scaler2=lambda x:x)
#         clf = LogisticRegression(C=c, penalty="l1", dual=False, class_weight='auto')
#         for iidx, (itrain, itest) in enumerate(inner_cv):
#             X_meg_inner_train = X_meg_train[itrain]
#             X_meg_val = X_meg_train[itest]
#             X_fmri_inner_train = X_fmri_train[itrain]
#             X_fmri_val = X_fmri_train[itest]
#             y_inner_train = y_train[itrain]
#             y_val = y_train[itest]

#             cca = cca.fit(X_fmri_inner_train,X_meg_inner_train)
#             fmri_train, meg_train = cca.transform(X_fmri_inner_train, 
#                                                   X_meg_inner_train)
#             fmri_val, meg_val = cca.transform(X_fmri_val, X_meg_val)
#             clf.fit(fmri_train[:, :ncomp], y_inner_train)
#             fmri_inner_preds.append(clf.predict(X_fmri_val[:, :ncomp]))
#             clf.fit(meg_train[:, :ncomp], y_inner_train)
#             meg_inner_preds.append(clf.predict(X_meg_val[:, :ncomp]))
#         fmri_val_scores.append(accuracy_score(y_train, fmri_inner_preds))
#         meg_val_scores.append(accuracy_score(y_train, meg_inner_preds))
#     avg_scores = (np.array(fmri_val_scores)+np.array(meg_val_scores))/2
#     c, ncomp, reg = params[np.argmax(avg_scores)]
#     print 'Best fold: C=%.2f, comp=%d, reg=%f'%(c,ncomp,reg)
#     best_params.append([c,ncomp,reg])

#     clf = LogisticRegression(C=c, penalty="l1", dual=False, class_weight='auto')
#     cca = kcca.KCCA(kernel, kernel, regularization=reg, decomp='full',
#                     method='kettering_method', scaler1=lambda x:x, 
#                     scaler2=lambda x:x)
#     cca = cca.fit(X_fmri_train,X_meg_train)
#     fmri_train, meg_train = cca.transform(X_fmri_train, X_meg_train)
#     fmri_test, meg_test = cca.transform(X_fmri_test, X_meg_test)
    
#     clf.fit(fmri_train[:, :ncomp], y_train)
#     fmri_preds.append(clf.predict(fmri_test[:, :ncomp]))
#     fmri_certainty.append(np.max(clf.predict_proba(fmri_test[:, :ncomp])))
    
#     clf.fit(meg_train[:, :ncomp], y_train)
#     meg_preds.append(clf.predict(meg_test[:, :ncomp]))
#     meg_certainty.append(np.max(clf.predict_proba(meg_test[:, :ncomp])))
# print 'Seed %s: fmri=%.2f, meg=%.2f'%(seed, 
#                                       accuracy_score(np.squeeze(fmri_preds),y),
#                                       accuracy_score(np.squeeze(meg_preds),y))
# fname = '%s_fmri_meg_%sVS%s'%(seed,g1,g2)
# np.savez(out_dir + fname, fmri_preds=fmri_preds, meg_preds=meg_preds,
#                           fmri_certainty=fmri_certainty, 
#                           meg_certainty=meg_certainty,
#                           y=y, params=params, best_params=best_params)