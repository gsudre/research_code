import mne
import numpy as np
import networkx as nx
import os
home = os.path.expanduser('~')


band_names = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
bands = [3]#range(len(band_names))
# subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
# data_dir = '/Users/sudregp/data/meg/sam/'
# g1_fname = home+'/data/meg/nv_subjs.txt'
# # g1_fname = home+'/data/meg/persistent_subjs.txt'
# # g1_fname = home+'/data/meg/remitted_subjs.txt'
# # g2_fname = home+'/data/meg/nv_subjs.txt'
# g2_fname = home+'/data/meg/persistent_subjs.txt'
# # g2_fname = home+'/data/meg/remitted_subjs.txt'
# g3_fname = home+'/data/meg/remitted_subjs.txt'
# sx_fname = home+'/data/meg/hi.txt'
# pval = .05
# cmethod=1

# fid = open(subjs_fname, 'r')
# subjs = [line.rstrip() for line in fid]

# # collect all the data and form networks
# nets = [[] for b in bands]
# for s in subjs:
#     print 'subject %d/%d'%(subjs.index(s)+1,len(subjs))
#     fname = data_dir + '%s_roi_connectivity.npy'%s
#     conn = np.load(fname)[()]
#     res = np.load(data_dir + '/perms/%s_roi_perm_connectivity.npy'%s)[()]
#     nperms=res.shape[1]
#     for bidx,bval in enumerate(bands):
#         data = conn[bval,cmethod,:,:].squeeze()
#         nfeats = conn.shape[2]
#         G = nx.Graph()
#         for node in range(nfeats):
#             G.add_node(node)
#         for j in range(nfeats):
#             for i in range(j+1,nfeats):
#                 # add an edge to the graph if the connection is significant
#                 if np.sum(data[i,j]<=res[bval,:,cmethod])/float(nperms) < pval:
#                     G.add_edge(i, j)
#         nets[bidx].append(G)

# # distribute the data into the different groups
# fid1 = open(g1_fname, 'r')
# fid2 = open(g2_fname, 'r')
# g1 = [line.rstrip() for line in fid1]
# g2 = [line.rstrip() for line in fid2]
# if len(g3_fname)>0:
#     fid3 = open(g3_fname, 'r')
#     g3 = [line.rstrip() for line in fid3]
# else:
#     g3 = []
# res = np.recfromtxt(sx_fname, delimiter='\t')
# sx = {}
# for rec in res:
#     sx[rec[0]] = rec[1]

# g1_data = [[] for b in bands]
# g2_data = [[] for b in bands]
# g3_data = [[] for b in bands]
# g1_subjs=[]
# g2_subjs=[]
# g3_subjs=[]
# g1_sx = []
# g2_sx = []
# for sidx, subj in enumerate(subjs):
#     print 'Gathering features for subject %d/%d'%(sidx+1,len(subjs))
#     for bidx,bval in enumerate(bands):
#         G = nets[bidx][sidx]

#         # select what kind of network metric we'll use
#         data = []
#         data.append(G.number_of_edges())
#         data.append(np.mean(nx.degree(G).values()))
#         data.append(nx.average_clustering(G))
#         data.append(nx.transitivity(G))
#         data.append(np.mean(nx.triangles(G).values()))
#         data.append(nx.average_node_connectivity(G))
#         data.append(np.mean(nx.betweenness_centrality(G).values()))
#         data.append(np.mean(nx.closeness_centrality(G).values()))
#         data.append(np.mean(nx.assortativity.average_degree_connectivity(G).values()))
#         data.append(np.mean(nx.assortativity.average_neighbor_degree(G).values()))
#         tmp = []
#         for g in nx.connected_component_subgraphs(G):
#             try:
#                 tmp.append(nx.average_shortest_path_length(g))
#             except:
#                 pass
#         data.append(np.mean(tmp))
 
#         if subj in g1:
#             g1_data[bidx].append(data)
#             if bidx==0:
#                 g1_subjs.append(subj)
#                 if subj in sx.keys():
#                     g1_sx.append(sx[subj])
#         elif subj in g2:
#             g2_data[bidx].append(data)
#             if bidx==0:
#                 g2_subjs.append(subj)
#                 if subj in sx.keys():
#                     g2_sx.append(sx[subj])
#         elif subj in g3:
#             g3_data[bidx].append(data)
#             g3_subjs.append(subj)

f0 = []
f1 = []
f2 = []
all_weights = []
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


    # ##############

    # RECURSIVE FEATURE ELIMINATION
    from sklearn.metrics import matthews_corrcoef, f1_score, roc_auc_score
    svc = LogisticRegression(penalty="l1", dual=False, class_weight='auto')
    # svc = SVC(kernel="linear")
    clf = svc
    nfeats = X.shape[1]
    nobs = X.shape[0]
    from sklearn.feature_selection import RFECV
    
    n_splits=20
    test_size = .1
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
        rfecv = RFECV(estimator=svc, step=1, cv=inner_cv,
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
    f0.append(f1_score(y, preds,pos_label=0))
    f1.append(f1_score(y, preds,pos_label=1))
    all_weights.append(weights)


    # # RECURSIVE FEATURE ELIMINATION 3 classes
    # from sklearn.metrics import matthews_corrcoef, f1_score, roc_auc_score
    # X = np.vstack([np.array(g3_data[bidx]), np.array(g2_data[bidx]), np.array(g3_data[bidx])])
    # y = np.hstack([np.zeros([len(g3_data[bidx])]),np.ones([len(g2_data[bidx])]),2*np.ones([len(g3_data[bidx])])])

    # imp = preprocessing.Imputer(missing_values='NaN', strategy='mean', axis=0)
    # imp.fit(X)
    # X = imp.transform(X)

    # X = preprocessing.scale(X)
    # svc = SVC(kernel="linear")#LogisticRegression(penalty="l1", dual=False, class_weight='auto')
    # clf = svc
    # nfeats = X.shape[1]
    # nobs = X.shape[0]
    # from sklearn.feature_selection import RFECV
    
    # n_splits=20
    # test_size = .1
    # cv = LeaveOneOut(nobs)
    # scores = []
    # preds = []
    # rand_preds = []
    # weights = 0
    # for oidx, (train, test) in enumerate(cv):
    #     print '%d/%d'%(oidx+1,nobs)
    #     X_train = X[train]
    #     X_test = X[test]
    #     y_train = y[train]
    #     y_test = y[test]
        
    #     inner_cv = StratifiedShuffleSplit(y_train, n_splits, test_size=test_size)
    #     rfecv = RFECV(estimator=svc, step=1, cv=inner_cv,
    #               scoring='f1')
    #     rfecv.fit(X_train, y_train)
    #     print("Optimal number of features : %d" % rfecv.n_features_)

    #     X_train = X_train[:, rfecv.support_]
    #     X_test = X_test[:, rfecv.support_]
    #     clf.fit(X_train, y_train)
    #     preds.append(clf.predict(X_test))
    #     cv_weights = np.zeros(nfeats)
    #     cv_weights[rfecv.support_] = np.abs(clf.coef_)
    #     weights += cv_weights
    # f0.append(f1_score(y, preds,pos_label=0))
    # f1.append(f1_score(y, preds,pos_label=1))
    # f2.append(f1_score(y, preds,pos_label=2))
    # all_weights.append(weights)

nperms=5000
f_rand=[f1_score(y, np.random.permutation(y), pos_label=1) for i in range(nperms)]
pvals = [np.sum(np.array(f_rand)>=m)/float(nperms) for m in f1]
print 'F-score(1):', f1
print 'F-score(1) pvals:', pvals
f_rand=[f1_score(y, np.random.permutation(y), pos_label=0) for i in range(nperms)]
pvals = [np.sum(np.array(f_rand)>=m)/float(nperms) for m in f0]
print 'F-score(0):', f0
print 'F-score(0) pvals:', pvals

# f_rand=[f1_score(y, np.random.permutation(y), pos_label=2) for i in range(nperms)]
# pvals = [np.sum(np.array(f_rand)>=m)/float(nperms) for m in f2]
# print 'F-score(2):', f2
# print 'F-score(2) pvals:', pvals
