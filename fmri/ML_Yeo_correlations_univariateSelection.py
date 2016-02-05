import numpy as np
import os
from scipy import stats
home = os.path.expanduser('~')

group_names = ['nvs','persistent','remission']
groups_fname = [home+'/data/fmri/joel_%s.txt'%g for g in group_names]
net = 1
data_folder = home+'/data/results/fmri_Yeo/net%d/'%net
nperms=5000


def print_scores(f, scores, title, pos_label=1):
    if pos_label is not None:
        rand_scores=[f(y, np.random.permutation(y), pos_label=pos_label) for i in range(nperms)]
    else:
        rand_scores=[f(y, np.random.permutation(y)) for i in range(nperms)]
    pvals = [np.sum(np.array(rand_scores)>=m)/float(nperms) for m in scores]   
    print title, ':', scores
    print title, 'pvals:', pvals


groups_subjs = []
for fname in groups_fname:
    fid = open(fname, 'r')
    subjs = [line.rstrip() for line in fid]
    fid.close()
    groups_subjs.append(subjs)

fid = open(data_folder+'regionsIn%d_clean.1D'%net, 'r')
rois = [line.rstrip() for line in fid]
fid.close()

print 'Loading data and computing correlations...'
corrs = []
for group in groups_subjs:
    subj_corrs = []
    for s in group:
        subj_data = []
        for r in rois:
            data = np.genfromtxt(data_folder+'%s_%sin%d.1D'%(s,r,net))
            if len(data) > 0:
                subj_data.append(data)
            else:
                print "bad data: %s in %s"%(s,r)
                subj_data.append([np.nan]*123)
        subj_corrs.append(np.corrcoef(subj_data))
    corrs.append(subj_corrs)

sens = []
spec = []
f1 = []
acc = []
prec = []
all_weights = []

nrois = len(rois)
il = np.tril_indices(nrois, -1)

from sklearn import preprocessing
from sklearn.linear_model import LogisticRegression
from sklearn.cross_validation import LeaveOneOut, StratifiedShuffleSplit, StratifiedKFold
from sklearn.grid_search import GridSearchCV
from sklearn.metrics import matthews_corrcoef, f1_score, roc_auc_score, recall_score, precision_score, accuracy_score

combs = [[0,1], [0,2], [1,2]]
for comb in combs:
    d1 = [m[il] for m in corrs[comb[0]]]
    d2 = [m[il] for m in corrs[comb[1]]]
    X = np.vstack([np.array(d1), np.array(d2)])
    y = np.hstack([np.zeros([len(d1)]),np.ones([len(d2)])])

    imp = preprocessing.Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(X)
    X = imp.transform(X)

    X = preprocessing.scale(X)

    nfeats = X.shape[1]
    nobs = X.shape[0]

    cs = [.1, .25, .5, .75, 1]#np.arange(.1,10,.5)

    # cv = LeaveOneOut(nobs)
    # inner_cv = LeaveOneOut(nobs-1)
    n_iter = 10
    test_size = .3
    cv = StratifiedShuffleSplit(y, n_iter=n_iter, test_size=test_size)

    scores = []
    preds = []
    rand_preds = []
    weights = 0
    for oidx, (train, test) in enumerate(cv):
        print '%d/%d'%(oidx+1,nobs)
        X_train = X[train]
        X_test = X[test]
        y_train = y[train]
        y_test = y[test]

        inner_cv = StratifiedShuffleSplit(y_train, n_iter=n_iter, test_size=test_size)

        c_val_scores = []
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
        # print 'Best C=%.2f'%(best_c)
        preds.append(clf.predict(X_test))
        weights += np.abs(clf.coef_)
    f1.append(f1_score(y, preds, pos_label=1))
    prec.append(precision_score(y, preds, pos_label=1))
    spec.append(recall_score(y, preds, pos_label=0))
    sens.append(recall_score(y, preds, pos_label=1))
    acc.append((accuracy_score(y, preds)))
    all_weights.append(weights)

    print_scores(f1_score, f1, 'F-score')
    print_scores(precision_score, prec, 'Precision')
    print_scores(recall_score, sens, 'Sensitivity/recall')
    print_scores(recall_score, spec, 'Specificity', pos_label=0)
    print_scores(accuracy_score, acc, 'Accuracy', pos_label=None)