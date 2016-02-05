# predicts symptoms using fMRI data
import os
import numpy as np
import sys
from time import time
from math import sqrt
home = os.path.expanduser('~')

phen = np.recfromcsv(home + '/data/overlap_resting/subjs.csv')
if len(sys.argv)>1:
    seed = sys.argv[1]
else:
    seed = 'net6_lSupra'
    
####
# open fMRI data
####
# load the order of subjects within the data matrix
subjs_fname = home + '/data/fmri/joel_all.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

X, inatt, hi = [], [], []
data_dir = home + '/data/results/fmri_Yeo/seeds/' + seed + '/' 
print 'Loading fMRI data...' 
data = np.genfromtxt(data_dir + 'joel_all_corr_downsampled.txt')
data = data[:,6:]  # removes x,y,z and i,j,k
for rec in phen:
    subj_idx = subjs.index('%04d'%rec[0])
    if rec['dx'] in ['persistent','remission']:
        X.append(data[:,subj_idx])
        hi.append(rec['hi'])
        inatt.append(rec['inatt'])
X = np.array(X)
# y = np.array([inatt, hi]).T
y = np.array(inatt)

########
# Starting cross-validation loops
######## 

from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.cross_validation import LeaveOneOut, ShuffleSplit
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import matthews_corrcoef, f1_score, roc_auc_score, recall_score, precision_score, accuracy_score, r2_score,mean_absolute_error
from sklearn.decomposition import FastICA, PCA, FactorAnalysis
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from scipy.stats import randint as sp_randint
from sklearn.grid_search import GridSearchCV, RandomizedSearchCV
from sklearn.dummy import DummyRegressor
from sklearn import manifold

########
# fmri classification
########
nfolds = 40
X = preprocessing.scale(X)
cv = ShuffleSplit(len(y),n_iter=nfolds,test_size=.3)
# preds is a list where the first index is the fold. Same thing for certainty
preds = []
certainty = []
accs = []
test_scores = []
train_scores = []
dummy_scores = []
nfeats = X.shape[1]
# specify parameters and distributions to sample from
param_dist = {#"max_depth": [3, 10, 100, None],
                "n_estimators": [500, 1000],
              "max_features": [50, int(sqrt(nfeats))],
              # "min_samples_split": sp_randint(1, 11),
              # "min_samples_leaf": sp_randint(1, 11),
              #"bootstrap": [True, False]}
              }
clf = RandomForestRegressor(n_jobs=-1)

# run randomized search
n_iter_search = 30
search = RandomizedSearchCV(clf, param_distributions=param_dist,
                                   n_iter=n_iter_search, scoring='mean_absolute_error')
search = GridSearchCV(clf, param_grid=param_dist,
                           scoring='mean_absolute_error')

lle = manifold.LocallyLinearEmbedding(n_components=nfeats)
for oidx, (train, test) in enumerate(cv):
    # print '=========\ncv %d/%d\n========='%(oidx+1,nfolds)
    X_train, X_test = X[train], X[test]
    y_train, y_test = y[train], y[test]

    # X_train = lle.fit_transform(X_train)
    # X_test = lle.transform(X_test)

    search.fit(X_train, y_train)

    clf = search.best_estimator_
    clf.fit(X_train,y_train)
    test_scores.append(mean_absolute_error(clf.predict(X_test),y_test))
    train_scores.append(mean_absolute_error(clf.predict(X_train),y_train))

    clf = DummyRegressor(strategy='median')
    clf.fit(X_train, y_train)
    dummy_scores.append(mean_absolute_error(clf.predict(X_test), y_test))
print '\n', seed
print 'dummy: %.3f'%np.median(dummy_scores)
print 'test: %.3f'%np.median(test_scores)
print 'train: %.3f'%np.median(train_scores)