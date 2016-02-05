# predicts symptoms using MEG data
import os
import numpy as np
import sys
from math import sqrt
home = os.path.expanduser('~')

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]

phen = np.recfromcsv(home + '/data/overlap_resting/subjs.csv')
if len(sys.argv)>1:
    seed = sys.argv[1]
else:
    seed = 'net6_lSupra'
    
####
# open MEG data
####
band_X = [[] for i in range(len(bands))]
inatt, hi = [], []
data_dir = home + '/data/results/meg_Yeo/seeds/' + seed + '/'
print 'Loading MEG data...'
for bidx, b in enumerate(bands):
    data = np.load(data_dir+'/correlations_%s-%s.npy'%(b[0],b[1]))[()]
    for rec in phen:
        if rec['dx'] in ['persistent','remission']:
            band_X[bidx].append(data[rec[1]])
            if bidx==0:
                hi.append(rec['hi'])
                inatt.append(rec['inatt'])

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
y = np.array(inatt)
nfolds = 40
n_iter_search = 30
cv = ShuffleSplit(len(y),n_iter=nfolds,test_size=.3)
for bidx, b in enumerate(bands):
    X = np.array(band_X[bidx]).squeeze()
    imp = preprocessing.Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(X)
    X = imp.transform(X)
    X = preprocessing.scale(X)

    test_scores = []
    train_scores = []
    dummy_scores = []
    nfeats = X.shape[1]
    # specify parameters and distributions to sample from
    param_dist = {#"max_depth": [3, 10, 100, None],
                    "n_estimators": [500, 1000],
                  "max_features": [50, int(sqrt(nfeats))],
                  }
    clf = RandomForestRegressor(n_jobs=-1)

    # run randomized search
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
    print '\n', seed, b
    print 'dummy: %.3f'%np.median(dummy_scores)
    print 'test: %.3f'%np.median(test_scores)
    print 'train: %.3f'%np.median(train_scores)
