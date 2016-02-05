# classifies MEG and fMRI subjects in one of the 3 groups (pairwise), and then
# try the classification using the combination of data
import os
import numpy as np
import sys
from time import time
from math import sqrt
home = os.path.expanduser('~')

phen = np.recfromcsv(home + '/data/overlap_resting/subjs.csv')
out_dir = home + '/data/results/rest_classification/'
if len(sys.argv)>1:
    seed, g1, g2 = sys.argv[1:]
else:
    seed = 'net6_lSupra'
    g1 = 'persistent'
    g2 = 'NV'

####
# open fMRI data
####
# load the order of subjects within the data matrix
subjs_fname = home + '/data/fmri/joel_all.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

g1_data, g2_data = [], []
g1_subjs, g2_subjs = [], []
data_dir = home + '/data/results/fmri_Yeo/seeds/' + seed + '/' 
print 'Loading fMRI data...' 
data = np.genfromtxt(data_dir + 'joel_all_corr_downsampled.txt')
data = data[:,6:]  # removes x,y,z and i,j,k
for rec in phen:
    subj_idx = subjs.index('%04d'%rec[0])
    if rec[2] == g1:
        g1_data.append(data[:,subj_idx])
        g1_subjs.append(subjs[subj_idx])
    elif rec[2] == g2:
        g2_data.append(data[:,subj_idx])
        g2_subjs.append(subjs[subj_idx])
g1_data = np.array(g1_data)
g2_data = np.array(g2_data)

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
cs = [.1, .5, 1, 5, 10]
ncomps = [2, 5, 10, 20, 50, 100]
params = [[i,j] for i in cs for j in ncomps]
best_params = []

from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.cross_validation import LeaveOneOut, StratifiedShuffleSplit, StratifiedKFold
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import matthews_corrcoef, f1_score, roc_auc_score, recall_score, precision_score, accuracy_score
from sklearn.decomposition import FastICA, PCA, FactorAnalysis
from sklearn.ensemble import RandomForestClassifier
from scipy.stats import randint as sp_randint
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
from sklearn.dummy import DummyClassifier

########
# fmri classification
########
nfolds = 20
X = np.vstack([g1_data, g2_data])
y = np.array(labels)
X = preprocessing.scale(X)
cv = StratifiedShuffleSplit(y,n_iter=nfolds,test_size=.1)
# preds is a list where the first index is the fold. Same thing for certainty
preds = []
certainty = []
accs = []
test_scores = []
train_scores = []
dummy_scores = []
nfeats = X.shape[1]
# specify parameters and distributions to sample from
param_dist = {"max_depth": [3, 10, 100, None],
                "n_estimators": [20, 100, 1000],
              "max_features": [int(sqrt(nfeats))],
              # "min_samples_split": sp_randint(1, 11),
              # "min_samples_leaf": sp_randint(1, 11),
              "bootstrap": [True, False],
              "criterion": ["gini", "entropy"]}
# grid_search = GridSearchCV(clf, param_grid=param_grid)
clf = RandomForestClassifier(n_jobs=-1)

# run randomized search
n_iter_search = 30
random_search = RandomizedSearchCV(clf, param_distributions=param_dist,
                                   n_iter=n_iter_search, scoring='f1')
lle = manifold.LocallyLinearEmbedding(n_components=nfeats)
for oidx, (train, test) in enumerate(cv):
    print '=========\ncv %d/%d\n========='%(oidx+1,nfolds)
    X_train, X_test = X[train], X[test]
    y_train, y_test = y[train], y[test]

    # X_train = lle.fit_transform(X_train)
    # X_test = lle.transform(X_test)

    random_search.fit(X_train, y_train)

    clf = random_search.best_estimator_
    clf.fit(X_train,y_train)
    test_scores.append(f1_score(clf.predict(X_test),y_test, pos_label=0))
    train_scores.append(f1_score(clf.predict(X_train),y_train, pos_label=0))

    clf = DummyClassifier(strategy='most_frequent')
    clf.fit(X_train, y_train)
    dummy_scores.append(f1_score(clf.predict(X_test), y_test, pos_label=0))