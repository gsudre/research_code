''' Checks whether there is a group difference in the connectivity '''

import numpy as np
import os
home = os.path.expanduser('~')


band_names = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
bands = [3]#range(len(band_names))
g1_fname = home+'/data/meg/remitted_subjs.txt'
g2_fname = home+'/data/meg/persistent_subjs.txt'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = home+'/data/meg/sam/seed/'
cmethod = 5

seed_name = 'mPFC'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]

g1_data = [[] for b in bands]
g2_data = [[] for b in bands]
g3_data = [[] for b in bands]
g1_subjs=[]
g2_subjs=[]
for s in subjs:
    if s not in ['WZYXTRYY'] or (s not in ['WZYXTRYY'] and seed_name=='mPFC'):
        fname = data_dir + '%s_%s_connectivity.npy'%(s,seed_name)
        conn = np.load(fname)[()]
        for b in range(len(bands)):
            data = conn[:,b]
            if s in g1:
                g1_data[b].append(data.T)
                if b==0:
                    g1_subjs.append(s)
            elif s in g2:
                g2_data[b].append(data.T)
                if b==0:
                    g2_subjs.append(s)

res = []
nbands = len(bands)
for bidx,band in enumerate(bands):
    print band_names[band]
    X = np.vstack([np.array(g1_data[bidx]), np.array(g2_data[bidx])])
    y = np.hstack([np.zeros([len(g1_data[bidx])]),np.ones([len(g2_data[bidx])])])
    
    from sklearn import preprocessing
    from sklearn.linear_model import LogisticRegression
    from sklearn.svm import SVC
    from sklearn.cross_validation import LeaveOneOut, StratifiedShuffleSplit, StratifiedKFold
    from sklearn.grid_search import GridSearchCV

    imp = preprocessing.Imputer(missing_values='NaN', strategy='mean', axis=0)
    imp.fit(X)
    X = imp.transform(X)

    # X = preprocessing.normalize(X, norm='l2')
    X = preprocessing.scale(X)


    ###############

    # nfeats = X.shape[1]
    # nobs = X.shape[0]
    
    # # cv = LeaveOneOut(nobs)
    # n_splits=50
    # test_size = .05
    # cv = StratifiedShuffleSplit(y, n_splits, test_size=test_size)
    # cs = np.arange(.1,1,.1)
    # scores = []
    # max_label = np.argmax([sum(y==0),sum(y==1)])
    # chance = sum(y==max_label)/float(nobs)
    # print 'Chance = %.3f'%chance
    # all_weights = []
    # for oidx, (train, test) in enumerate(cv):
    #     X_train = X[train]
    #     X_test = X[test]
    #     y_train = y[train]
    #     y_test = y[test]
    #     scaler = preprocessing.StandardScaler().fit(X_train)
    #     X_train = scaler.transform(X_train)
    #     X_test = scaler.transform(X_test)
    #     inner_cv = StratifiedShuffleSplit(y_train, n_splits, test_size=test_size)
    #     c_val_scores = []
    #     c_train_scores = []
    #     weights = 0
    #     for c in cs:
    #         clf_cv = LogisticRegression(C=c, penalty="l1", dual=False, class_weight='auto')
    #         cur_c_val_scores = []
    #         cur_c_train_scores = []
    #         for iidx, (itrain, itest) in enumerate(inner_cv):
    #             X_inner_train = X_train[itrain]
    #             X_val = X_train[itest]
    #             y_inner_train = y_train[itrain]
    #             y_val = y_train[itest]
    #             scaler = preprocessing.StandardScaler().fit(X_inner_train)
    #             X_inner_train = scaler.transform(X_inner_train)
    #             X_val = scaler.transform(X_val)
    #             clf_cv.fit(X_inner_train, y_inner_train)
    #             pred = clf_cv.score(X_val, y_val)
    #             cur_c_val_scores.append(pred)
    #             cur_c_train_scores.append(np.mean(clf_cv.score(X_inner_train, y_inner_train)))
    #             weights += clf_cv.coef_
    #         c_val_scores.append(np.mean(cur_c_val_scores))
    #         c_train_scores.append(np.mean(cur_c_train_scores))
    #         all_weights.append(weights)
    #     best_c = cs[np.argmax(c_val_scores)]
    #     clf = LogisticRegression(C=best_c, penalty="l1", dual=False, class_weight='auto')
    #     clf.fit(X_train,y_train)
    #     pred = clf.score(X_test, y_test)
    #     scores.append(pred)
    #     # print 'CV %d/%d, c=%.2f, %d/%d features, %.3f train acc, %.3f val acc, %.3f test acc'%(oidx+1,len(cv),best_c, clf.transform(X_train).shape[1], nfeats, c_train_scores[np.argmax(c_val_scores)], np.max(c_val_scores), scores[-1])
    #     print 'CV %d/%d, c=%.2f, %.3f train acc, %.3f val acc, %.3f test acc'%(oidx+1,len(cv),best_c,c_train_scores[np.argmax(c_val_scores)],np.max(c_val_scores), scores[-1])
    # print np.mean(scores), '+-', np.std(scores)
    # print 'Chance = %.3f'%chance
    ##############


    ##############

    # nfolds = 20
    # tsize=.2
    # C_range = 10.0 ** np.arange(-2, 9)
    # gamma_range = 10.0 ** np.arange(-5, 4)
    # param_grid = dict(gamma=gamma_range, C=C_range, class_weight=['auto'])
    # cv = StratifiedShuffleSplit(y, nfolds, test_size=tsize)
    # nfeats = X.shape[1]
    # nobs = X.shape[0]
    
    # scores = []
    # max_label = np.argmax([sum(y==0),sum(y==1)])
    # chance = sum(y==max_label)/float(nobs)
    # print 'Chance = %.3f'%chance
    # for oidx, (train, test) in enumerate(cv):
    #     X_train = X[train]
    #     X_test = X[test]
    #     y_train = y[train]
    #     y_test = y[test]
    #     scaler = preprocessing.StandardScaler().fit(X_train)
    #     X_train = scaler.transform(X_train)
    #     X_test = scaler.transform(X_test)
    #     inner_cv = StratifiedShuffleSplit(y_train, nfolds, test_size=tsize)
    #     grid = GridSearchCV(SVC(), param_grid=param_grid, cv=inner_cv)
    #     grid.fit(X_train, y_train)
    #     clf = grid.best_estimator_
    #     clf.fit(X_train,y_train)
    #     pred = clf.score(X_test, y_test)
    #     scores.append(pred)
    #     print 'CV %d/%d'%(oidx+1,len(cv))
    # print np.mean(scores), '+-', np.std(scores)
    # print 'Chance = %.3f'%chance

    # ##############

    # nfolds = 10
    # nfeats = X.shape[1]
    # nobs = X.shape[0]
    # from sklearn.cross_validation import KFold
    # from sklearn.metrics import roc_auc_score
    # # cv = KFold(nobs, n_folds=nfolds)
    # cv = StratifiedKFold(y, n_folds=nfolds)
    # from sklearn import svm
    # nus = np.arange(.1,1,.2)

    # cv_acc = []
    # for oidx, (train, test) in enumerate(cv):
    #     X_train = X[train]
    #     X_test = X[test]
    #     y_train = y[train]
    #     y_test = y[test]
    #     # inner_cv = KFold(len(train), n_folds=nfolds)
    #     inner_cv = StratifiedKFold(y_train, n_folds=nfolds)
    #     inner_acc=[]
    #     for iidx, (itrain, itest) in enumerate(inner_cv):
    #         X_inner_train = X_train[itrain]
    #         X_val = X_train[itest]
    #         y_inner_train = y_train[itrain]
    #         y_val = y_train[itest]
    #         scaler = preprocessing.StandardScaler().fit(X_inner_train)
    #         X_inner_train = scaler.transform(X_inner_train)
    #         X_val = scaler.transform(X_val)
    #         params_acc = []
    #         for nu in nus:
    #             clf = svm.OneClassSVM(nu=nu, kernel="linear")
    #             clfo = svm.SVC(C=1, kernel='linear', class_weight='auto', probability=False)
    #             clfn = svm.SVC(C=1, kernel='linear', class_weight='auto', probability=False)
    #             clf.fit(X_inner_train)
    #             overlap = clf.predict(X_inner_train)==1
    #             nonoverlap = clf.predict(X_inner_train)==-1
    #             clfo.fit(X_inner_train[overlap],y_inner_train[overlap])
    #             clfn.fit(X_inner_train[nonoverlap],y_inner_train[nonoverlap])
    #             res = []
    #             for i in range(len(y_val)):
    #                 if clf.predict(X_val[i])==1:
    #                     res.append(clfo.predict(X_val[i]))
    #                 else:
    #                     res.append(clfn.predict(X_val[i]))
    #             params_acc.append(roc_auc_score(y_val,res,average='weighted'))
    #         inner_acc.append(params_acc)
    #     inner_acc = np.array(inner_acc)
    #     best_nu = nus[np.argmax(np.mean(inner_acc,axis=0))]
    #     clf.fit(X_train)
    #     overlap = clf.predict(X_train)==1
    #     nonoverlap = clf.predict(X_train)==-1
    #     clfo.fit(X_train[overlap],y_train[overlap])
    #     clfn.fit(X_train[nonoverlap],y_train[nonoverlap])
    #     res = []
    #     for i in range(len(y_test)):
    #         if clf.predict(X_test[i])==1:
    #             res.append(clfo.predict(X_test[i]))
    #         else:
    #             res.append(clfn.predict(X_test[i]))
    #     cv_acc.append(roc_auc_score(y_test,res,average='weighted'))
    # print np.mean(cv_acc), '+-', np.std(cv_acc)


    # ##############

    # RECURSIVE FEATURE ELIMINATION

    svc = SVC(kernel="linear")
    clf = svc
    nfeats = X.shape[1]
    nobs = X.shape[0]
    from sklearn.feature_selection import RFECV
    
    n_splits=10
    test_size = .1
    cv = LeaveOneOut(nobs)#StratifiedShuffleSplit(y, n_splits, test_size=test_size)
    scores = []
    all_weights = []
    for oidx, (train, test) in enumerate(cv):
        print '%d/%d'%(oidx+1,nobs)
        X_train = X[train]
        X_test = X[test]
        y_train = y[train]
        y_test = y[test]
        
        inner_cv = StratifiedShuffleSplit(y_train, n_splits, test_size=test_size)
        rfecv = RFECV(estimator=svc, step=.05, cv=inner_cv,
                  scoring='accuracy')
        rfecv.fit(X_train, y_train)
        print("Optimal number of features : %d" % rfecv.n_features_)

        X_train = X_train[:, rfecv.support_]
        X_test = X_test[:, rfecv.support_]
        clf.fit(X_train, y_train)
        scores.append(clf.score(X_test,y_test))
    print 'Overall accuracy:', np.mean(scores)
    ##############

n1 = len(g1_data[0])
n2 = len(g2_data[0])
print 'size1 =', n1
print 'size2 =', n2
print 'g1 =',g1_fname
print 'g2 =',g2_fname
m = ['pli','imcoh','plv','wpli','pli2_unbiased','wpli2_debiased']
print m[cmethod]
print 'hemi:', hemi
# for i,j in enumerate(res):
#     print bands[i], ':', j[0]

def map_connections(adj, cl):
    conn = np.nonzero(adj==cl)
    conn_list = []
    for i in range(len(conn[0])):
        edge = [conn[0][i], conn[1][i]]
        edge_bvals = [rois[idx[j]] for j in edge]
        edge_brodmann = [key for j in edge_bvals for key,val in areas.iteritems() if j in val]
        edge_str = []
        for j in [0,1]:
            if areas[edge_brodmann[j]].index(edge_bvals[j])==0:
                h='L'
            else:
                h='R'
            edge_str.append('%d-%s'%(edge_brodmann[j],h))
        edge_str.sort()
        if edge_str not in conn_list:   
            conn_list.append(edge_str)
    print conn_list


def plot_group_diff(adj, cl=1):
    conn = np.nonzero(adj==cl)
    conn_list = []
    for i in range(len(conn[0])):
        edge = [conn[0][i], conn[1][i]]
        edge.sort()
        if edge not in conn_list:   
            conn_list.append(edge)
    print conn_list
    xp = []
    yp = []
    for i in conn_list:
        xp.append(x[i[0],i[1],:])
        yp.append(y[i[0],i[1],:])
    xp = np.array(xp)
    yp = np.array(yp)
    print xp.shape
    print yp.shape
    for i in range(len(conn_list)):
        figure()
        boxplot([xp[i,:], yp[i,:]])
        title('%d'%i)
    figure()
    boxplot([xp.mean(axis=0), yp.mean(axis=0)])
    title('mean')