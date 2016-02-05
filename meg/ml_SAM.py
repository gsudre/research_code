''' Checks whether there is a group difference in the connectivity '''

import numpy as np
import os
home = os.path.expanduser('~')


band_names = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
bands = range(len(band_names))
g1_fname = home+'/data/meg/nv_subjs.txt'
g2_fname = home+'/data/meg/persistent_subjs.txt'
g3_fname = home+'/data/meg/remitted_subjs.txt'
sx_fname = home+'/data/meg/inatt.txt'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = home+'/data/meg/sam/'
cmethod = 5
hemi = -1
comb_bands = False
do_mean=False

# list of lists, indicating which ROIs are grouped together, avoiding non-meaningful connections. Set all2all=True if interested in doing each ROI by itself
selected_labels = []
# selected_labels = [10,9,32,24,23,31,30,39,40] #DMN
# selected_labels = [[32,24],[23],[39]] #DMN-select
# selected_labels = [[8], [39, 40, 7]] # dorsal
# selected_labels = [[39,40,41,42], [44,45,46]] #ventral
# selected_labels = [[39], [44,45,46]] #ventral-select
# selected_labels = [[46,9], [8], [44,45,47], [6], [7, 5]] # cognitive control
# selected_labels = [32,24,25,10,11,47] #affective
selected_labels = [1,10,11,17,18,19,2,20,21,22,23,24,25,3,31,32,37,38,39,4,40,41,42,43,44,45,46,47,5,6,7,8,9] #Hillebrand, 33 only had one voxel
# selected_labels = [37,5,39,6,4,46]


fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
if len(g3_fname)>0:
    fid3 = open(g3_fname, 'r')
    g3 = [line.rstrip() for line in fid3]
else:
    g3 = []

res = np.recfromtxt(sx_fname, delimiter='\t')
sx = {}
for rec in res:
    sx[rec[0]] = rec[1]

areas = np.load(home+'/sam/areas.npy')[()]
res = np.load(home+'/sam/rois.npz')
rois = list(res['rois'])
nlabels=len(rois)

if hemi>=0:
    if len(selected_labels)>0:
        brodmann_val = [areas[l][hemi] for l in selected_labels]
    else:
        if hemi==0:
            brodmann_val = rois[1:-1:2]
        else:
            brodmann_val = rois[0:-1:2]
    idx = [rois.index(b) for b in brodmann_val]
    delme = np.setdiff1d(range(nlabels),idx)
    nlabels -= len(delme) 
else:
    if len(selected_labels)>0:
        brodmann_val = [i for l in selected_labels for i in areas[l]]
    else:
        brodmann_val = rois
    idx = [rois.index(b) for b in brodmann_val]
    delme = np.setdiff1d(range(nlabels),idx)
    nlabels -= len(delme) 

g1_data = [[] for b in bands]
g2_data = [[] for b in bands]
g3_data = [[] for b in bands]
g1_subjs=[]
g2_subjs=[]
g3_subjs=[]
g1_sx = []
g2_sx = []
il = np.tril_indices(nlabels, k=-1)
for s in subjs:
    fname = data_dir + '%s_roi_connectivity.npy'%s
    conn = np.load(fname)[()]
    if not comb_bands:
        nbands = len(bands)
        for bidx,bval in enumerate(bands):
            data = conn[bval][cmethod][:,:].squeeze()
            data = np.delete(data, delme, axis=0)
            data = np.delete(data, delme, axis=1) 
            if do_mean:
                ul = np.triu_indices(nlabels, k=1)
                data[ul] = data[il]
                data = np.mean(data,axis=0)
            else:
                data = data[il]
            if s in g1:
                g1_data[bidx].append(data)
                if bidx==0:
                    g1_subjs.append(s)
                    # g1_sx.append(sx[s])
            elif s in g2:
                g2_data[bidx].append(data)
                if bidx==0:
                    g2_subjs.append(s)
                    # g2_sx.append(sx[s])
            elif s in g3:
                g3_data[bidx].append(data)
                if bidx==0:
                    g3_subjs.append(s)
    else:
        nbands=1
        subj_data = []
        for bidx,bval in enumerate(bands):
            data = conn[bval][cmethod][:,:].squeeze()
            data = np.delete(data, delme, axis=0)
            data = np.delete(data, delme, axis=1)
            if do_mean:
                ul = np.triu_indices(nlabels, k=1)
                data[ul] = data[il]
                data = np.mean(data,axis=0)
            else:
                data = data[il]
            subj_data.append(data) 
        if s in g1:
            g1_data[0].append(np.array(subj_data).flatten())
            g1_subjs.append(s)
            # g1_sx.append(sx[s])
        elif s in g2:
            g2_data[0].append(np.array(subj_data).flatten())
            g2_subjs.append(s)
            # g2_sx.append(sx[s])
        elif s in g3:
            g3_data[0].append(np.array(subj_data).flatten())
            g3_subjs.append(s)

res = []

f0 = []
f1 = []
f2 = []
all_weights = []
for b in range(nbands):
    print band_names[bands[b]]
    X = np.vstack([np.array(g1_data[b]), np.array(g3_data[b])])
    y = np.hstack([np.zeros([len(g1_data[b])]),np.ones([len(g3_data[b])])])
    
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

    # RECURSIVE FEATURE ELIMINATION
    from sklearn.metrics import matthews_corrcoef, f1_score, roc_auc_score
    svc = LogisticRegression(penalty="l1", dual=False, class_weight='auto')
    # svc = SVC(kernel="linear")
    clf = svc
    nfeats = X.shape[1]
    nobs = X.shape[0]
    from sklearn.feature_selection import RFECV
    
    n_splits=20
    test_size = .05
    cv = LeaveOneOut(nobs)#StratifiedShuffleSplit(y, n_splits, test_size=test_size)
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
        
        inner_cv = StratifiedShuffleSplit(y_train, n_splits, test_size=test_size)
        rfecv = RFECV(estimator=svc, step=.05, cv=inner_cv,
                  scoring='f1')
        rfecv.fit(X_train, y_train)
        print("Optimal number of features : %d" % rfecv.n_features_)

        X_train = X_train[:, rfecv.support_]
        X_test = X_test[:, rfecv.support_]
        clf.fit(X_train, y_train)
        preds.append(clf.predict(X_test))
        cv_weights = np.zeros(nfeats)
        cv_weights[rfecv.support_] = np.abs(clf.coef_)
        weights += cv_weights
    # matt.append(matthews_corrcoef(y, preds))
    f0.append(f1_score(y, preds,pos_label=0))
    f1.append(f1_score(y, preds,pos_label=1))
    all_weights.append(weights)
    # matt.append(roc_auc_score(y,scores,average='weighted'))


nperms=5000
# matt_rand=[matthews_corrcoef(y, np.random.permutation(y)) for i in range(nperms)]
# matt_rand=[f1_score(y, np.random.permutation(y)) for i in range(nperms)]
f_rand=[f1_score(y, np.random.permutation(y), pos_label=1) for i in range(nperms)]
# pvals = [np.sum(np.abs(np.array(matt_rand))>=abs(m))/float(nperms) for m in matt]
pvals = [np.sum(np.array(f_rand)>=m)/float(nperms) for m in f1]
print 'F-score(1):', f1
print 'F-score(1) pvals:', pvals
f_rand=[f1_score(y, np.random.permutation(y), pos_label=0) for i in range(nperms)]
# pvals = [np.sum(np.abs(np.array(matt_rand))>=abs(m))/float(nperms) for m in matt]
pvals = [np.sum(np.array(f_rand)>=m)/float(nperms) for m in f0]
print 'F-score(0):', f0
print 'F-score(0) pvals:', pvals

# # RECURSIVE FEATURE ELIMINATION 3 classes
#     from sklearn.metrics import matthews_corrcoef, f1_score, roc_auc_score
#     X = np.vstack([np.array(g3_data[bidx]), np.array(g2_data[bidx]), np.array(g3_data[bidx])])
#     y = np.hstack([np.zeros([len(g3_data[bidx])]),np.ones([len(g2_data[bidx])]),2*np.ones([len(g3_data[bidx])])])

#     imp = preprocessing.Imputer(missing_values='NaN', strategy='mean', axis=0)
#     imp.fit(X)
#     X = imp.transform(X)

#     X = preprocessing.scale(X)
#     svc = LogisticRegression(penalty="l1", dual=False, class_weight='auto')
#     clf = svc
#     nfeats = X.shape[1]
#     nobs = X.shape[0]
#     from sklearn.feature_selection import RFECV
    
#     n_splits=20
#     test_size = .05
#     cv = LeaveOneOut(nobs)
#     scores = []
#     preds = []
#     rand_preds = []
#     weights = 0
#     for oidx, (train, test) in enumerate(cv):
#         print '%d/%d'%(oidx+1,nobs)
#         X_train = X[train]
#         X_test = X[test]
#         y_train = y[train]
#         y_test = y[test]
        
#         inner_cv = StratifiedShuffleSplit(y_train, n_splits, test_size=test_size)
#         rfecv = RFECV(estimator=svc, step=.05, cv=inner_cv,
#                   scoring='f1')
#         rfecv.fit(X_train, y_train)
#         print("Optimal number of features : %d" % rfecv.n_features_)

#         X_train = X_train[:, rfecv.support_]
#         X_test = X_test[:, rfecv.support_]
#         clf.fit(X_train, y_train)
#         preds.append(clf.predict(X_test))
#         cv_weights = np.zeros(nfeats)
#         cv_weights[rfecv.support_] = np.abs(clf.coef_)
#         weights += cv_weights
#     f0.append(f1_score(y, preds,pos_label=0))
#     f1.append(f1_score(y, preds,pos_label=1))
#     f2.append(f1_score(y, preds,pos_label=2))
#     all_weights.append(weights)

# nperms=5000
# f_rand=[f1_score(y, np.random.permutation(y), pos_label=1) for i in range(nperms)]
# pvals = [np.sum(np.array(f_rand)>=m)/float(nperms) for m in f1]
# print 'F-score(1):', f1
# print 'F-score(1) pvals:', pvals
# f_rand=[f1_score(y, np.random.permutation(y), pos_label=0) for i in range(nperms)]
# pvals = [np.sum(np.array(f_rand)>=m)/float(nperms) for m in f0]
# print 'F-score(0):', f0
# print 'F-score(0) pvals:', pvals

# f_rand=[f1_score(y, np.random.permutation(y), pos_label=2) for i in range(nperms)]
# pvals = [np.sum(np.array(f_rand)>=m)/float(nperms) for m in f2]
# print 'F-score(2):', f2
# print 'F-score(2) pvals:', pvals
    # ###############

    # nfeats = X.shape[1]
    # nobs = X.shape[0]
    
    # # cv = LeaveOneOut(nobs)
    # n_splits=50
    # test_size = .05
    # cv = StratifiedShuffleSplit(y, n_splits, test_size=test_size)
    # cs = np.arange(.5,4,.1)
    # scores = []
    # max_label = np.argmax([sum(y==0),sum(y==1)])
    # chance = sum(y==max_label)/float(nobs)
    # print 'Chance = %.3f'%chance
    # for oidx, (train, test) in enumerate(cv):
    #     X_train = X[train]
    #     X_test = X[test]
    #     y_train = y[train]
    #     y_test = y[test]
    #     print sum(y_test==1),sum(y_test==0)
    #     scaler = preprocessing.StandardScaler().fit(X_train)
    #     X_train = scaler.transform(X_train)
    #     X_test = scaler.transform(X_test)
    #     # inner_cv = LeaveOneOut(len(train))
    #     inner_cv = StratifiedShuffleSplit(y_train, n_splits, test_size=test_size)
    #     c_val_scores = []
    #     c_train_scores = []
    #     for c in cs:
    #         clf = LogisticRegression(C=c, penalty="l1", dual=False, class_weight='auto')
    #         # clf = SVC(C=c, kernel='linear', class_weight='auto', probability=True)
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
    #             X_val = np.array([np.mean(X_val[y_val==0],axis=0), np.mean(X_val[y_val==1],axis=0)])
    #             y_val = np.array([0,1])
    #             clf.fit(X_inner_train, y_inner_train)
    #             pred = clf.score(X_val, y_val)
    #             cur_c_val_scores.append(pred)
    #             cur_c_train_scores.append(np.mean(clf.score(X_inner_train, y_inner_train)))
    #         c_val_scores.append(np.mean(cur_c_val_scores))
    #         c_train_scores.append(np.mean(cur_c_train_scores))
    #     best_c = cs[np.argmax(c_val_scores)]
    #     clf = LogisticRegression(C=best_c, penalty="l1", dual=False, class_weight='auto')
    #     # clf = SVC(C=best_c, kernel='linear', class_weight='auto', probability=True)
    #     clf.fit(X_train,y_train)
    #     X_test = np.array([np.mean(X_test[y_test==0],axis=0), np.mean(X_test[y_test==1],axis=0)])
    #     y_test = np.array([0,1])
    #     pred = clf.score(X_test, y_test)
    #     scores.append(pred)
    #     # print 'CV %d/%d, c=%.2f, %d/%d features, %.3f train acc, %.3f val acc, %.3f test acc'%(oidx+1,len(cv),best_c, clf.transform(X_train).shape[1], nfeats, c_train_scores[np.argmax(c_val_scores)], np.max(c_val_scores), scores[-1])
    #     print 'CV %d/%d, c=%.2f, %.3f train acc, %.3f val acc, %.3f test acc'%(oidx+1,len(cv),best_c,c_train_scores[np.argmax(c_val_scores)],np.max(c_val_scores), scores[-1])
    # print np.mean(scores), '+-', np.std(scores)
    # print 'Chance = %.3f'%chance
    # ##############


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
    #     print sum(y_test==1),sum(y_test==0)
    #     scaler = preprocessing.StandardScaler().fit(X_train)
    #     X_train = scaler.transform(X_train)
    #     X_test = scaler.transform(X_test)
    #     inner_cv = StratifiedShuffleSplit(y_train, nfolds, test_size=tsize)
    #     grid = GridSearchCV(SVC(), param_grid=param_grid, cv=inner_cv)
    #     grid.fit(X_train, y_train)
    #     clf = grid.best_estimator_
    #     clf.fit(X_train,y_train)
    #     X_test = np.array([np.mean(X_test[y_test==0],axis=0), np.mean(X_test[y_test==1],axis=0)])
    #     y_test = np.array([0,1])
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


    ##############

    

    ##############

# n1 = len(g1_data[0])
# n2 = len(g2_data[0])
# print 'size1 =', n1
# print 'size2 =', n2
# print 'g1 =',g1_fname
# print 'g2 =',g2_fname
# m = ['pli','imcoh','plv','wpli','pli2_unbiased','wpli2_debiased']
# print m[cmethod]
# print 'hemi:', hemi
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