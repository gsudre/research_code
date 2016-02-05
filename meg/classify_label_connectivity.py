''' Checks whether there is a group difference in the connectivity map for a given seed '''

import mne
import numpy as np
from scipy import stats

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
g1_fname = '/Users/sudregp/data/meg/remitted_subjs.txt'
g2_fname = '/Users/sudregp/data/meg/persistent_subjs.txt'
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_5segs13p654.txt'
data_dir = '/Users/sudregp/data/meg/connectivity/MNE/'
lmethod = 'pca_flip'
cmethod = 5

selected_labels = []
# selected_labels = ['isthmuscingulate-rh', 'superiorfrontal-rh', 'inferiorparietal-rh', 'isthmuscingulate-lh', 'superiorfrontal-lh', 'inferiorparietal-lh']
# selected_labels = ['isthmuscingulate-rh', 'superiorfrontal-rh', 'inferiorparietal-rh']

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]

print 'g1 =',g1_fname
print 'g2 =',g2_fname
m = ['pli','imcoh','plv','wpli','pli2_unbiased','wpli2_debiased']
print lmethod, '-', m[cmethod]

labels, label_colors = mne.labels_from_parc(subjs[0], parc='aparc')
nlabels=len(labels)
il = np.tril_indices(nlabels, k=-1)
if len(selected_labels)>0:
    label_names = [l.name for l in labels]
    idx = [l for s in selected_labels for l, label in enumerate(label_names) if label == s]
    keep = [False]*len(il[0])
    for i in idx:
        for j in idx:
            keep = keep | ((il[0]==i) & (il[1]==j))
    il = [il[0][keep], il[1][keep]]


g1_data = [[] for b in range(len(bands))]
g2_data = [[] for b in range(len(bands))]
for s in subjs:
    fname = data_dir + '%s-%s-pli-imcoh-plv-wpli-pli2_unbiased-wpli2_debiased.npy'%(s,lmethod)
    conn = np.load(fname)[()]
    for b in range(len(bands)):
        data = conn[cmethod][:,:,b]
        data = data[il]
        if s in g1:
            g1_data[b].append(data.T)
        elif s in g2:
            g2_data[b].append(data.T)

cnt=0
for b in range(len(bands)):
    x = np.array(g1_data[b])
    y = np.array(g2_data[b])
    val = [stats.ttest_ind(x[:,i],y[:,i])[1] for i in range(x.shape[1])]
    print bands[b]
    print 'Sources < .05 uncorrected:', sum(np.array(val)<.05)
    cnt+=sum(np.array(val)<.05)

n1 = len(g1_data[0])
n2 = len(g2_data[0])
print 'size1 =', n1
print 'size2 =', n2
print cnt

if n1>n2:
    weight = {0 : n1/float(n2)}
else:
    weight = {1 : n2/float(n1)}

for b, band in enumerate(bands):
    print band

    # Make arrays X and y such that :
    # X is 2d with X.shape[0] is the total number of observations to classify
    # y is filled with integers coding for the class to predict
    # We must have X.shape[0] equal to y.shape[0]
    X = np.vstack([np.matrix(g1_data[b]), np.matrix(g2_data[b])])
    y = np.hstack([np.zeros([len(g1_data[b])]),np.ones([len(g2_data[b])])])

    from sklearn import cross_validation
    from sklearn.linear_model import LogisticRegression
    from sklearn.cross_validation import LeaveOneOut 

    from sklearn import preprocessing
    X = preprocessing.scale(X)

    # cv = LeaveOneOut(X.shape[0])
    # clf_l1_LR = LogisticRegression(C=.01, penalty='l1', tol=0.01, class_weight='auto')
    # this_scores = cross_validation.cross_val_score(clf_l1_LR, X, y, cv=cv)
    # print np.mean(this_scores)

'''
    transform = feature_selection.SelectPercentile(feature_selection.f_classif)
    clf = Pipeline([('anova', transform), ('svc', svm.SVC(C=1.0))])

    ###############################################################################
    # Plot the cross-validation score as a function of percentile of features
    # score_means = list()
    # score_stds = list()
    # percentiles = (1, 3, 6, 10, 15, 20, 30, 40, 60, 80, 100)

    # for percentile in percentiles:
    #     clf.set_params(anova__percentile=percentile)
    #     # Compute cross-validation score using all CPUs
    #     this_scores = cross_validation.cross_val_score(clf, X, y, n_jobs=1)
    #     score_means.append(this_scores.mean())
    #     score_stds.append(this_scores.std())

    
    
    Xorig = X.copy()

    # # we have to normalize the data before supplying them to our classifier
    # X -= X.mean(axis=0)
    # X /= X.std(axis=0)
    X = preprocessing.scale(X)
    # from sklearn.decomposition import PCA
    # pca = PCA(n_components=2)
    # pca.fit(X)
    # print(pca.explained_variance_ratio_) 

    # prepare classifier
    from sklearn.svm import SVC, LinearSVC
    from sklearn.cross_validation import StratifiedShuffleSplit, ShuffleSplit, LeaveOneOut 
    # from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_selection import SelectKBest, f_classif
    from sklearn import linear_model

    # Define a monte-carlo cross-validation generator (reduce variance):
    n_splits = 10
    clf = SVC(C=1, kernel='linear')
    cv = StratifiedShuffleSplit(y, n_splits, test_size=0.3)
    cv = LeaveOneOut(X.shape[0])
    # cv = StratifiedKFold(y, n_splits)

    from sklearn.pipeline import Pipeline


    # enet = linear_model.ElasticNetCV()
    # alphas=np.array([  .001, .0001, .00001, .01, 0.1,   1. ,  10. ])
    # enet = linear_model.RidgeClassifierCV(class_weight=weight, alphas=alphas)


    # initialize score and feature weights result arrays
    n_feats = X.shape[1]
    scores = np.zeros(len(cv))
    # scores = np.zeros(X.shape[0])
    feature_weights = np.zeros([1, n_feats])

    pipe = Pipeline([
      ('feature_selection', LinearSVC(penalty="l1",dual=False)),
      ('classification', LinearSVC(penalty='l2'))
    ])
    clf.fit(X, y)


    cs = np.arange(.01,.4,.01)
    s = []
    for c in cs:
        print c
        clf_l1_LR = LogisticRegression(C=c, penalty='l1', tol=0.01, class_weight=None)
        # this_scores = cross_validation.cross_val_score(clf_l1_LR, X, y, cv=cv, n_jobs=1)

        s.append(np.mean(this_scores))


    cs = np.arange(.01,.1,.01)
    s = []
    for c in cs:
        print c
        clf_l1_LR = LogisticRegression(C=c, penalty='l1', tol=0.01, class_weight='auto')
        this_scores = cross_validation.cross_val_score(clf_l1_LR, X, y)
        s.append(np.mean(this_scores))



    from sklearn.cross_validation import LeaveOneOut
    cs = np.arange(.01,.1,.01)
    cv = LeaveOneOut(len(y))
    scores = []
    for ii, (train, test) in enumerate(cv):
        print ii
        s = []
        for c in cs:
            clf_l1_LR = LogisticRegression(C=c, penalty='l1', tol=0.01, class_weight='auto')
            this_scores = cross_validation.cross_val_score(clf_l1_LR, X[train], y[train], cv=LeaveOneOut(len(y[train])), n_jobs=1)
            s.append(np.mean(this_scores))
        c = cs[np.argmax(s)]
        print c
        print s
        clf_l1_LR = LogisticRegression(C=c, penalty='l1', tol=0.01, class_weight='auto')
        clf_l1_LR.fit(X[train], y[train])
        scores.append(clf_l1_LR.predict(X[test])==y[test])
    print np.mean(scores)



    feature_selection = SelectKBest(f_classif, k=50)  # take the best 500
    # to make life easier we will create a pipeline object
    pipe = Pipeline([('anova', feature_selection), ('svc', clf)])

    pipe = ExtraTreesClassifier(n_estimators=30)

    pipe = svm.SVC(kernel='rbf', gamma=0.7, C=1, class_weight=weight)

    # where the magic happens
    for ii, (train, test) in enumerate(cv):
        # enet.fit(X[train], y[train])
        pipe.fit(X[train], y[train])
        # y_pred = enet.predict(X[test])
        y_pred = pipe.predict(X[test])
        # y_pred[y_pred>0] = 1
        # y_pred[y_pred<1] = -1
        # pipe.fit(X[train], y[train])
        # y_pred = pipe.predict(X[test])
        # print enet.alpha_
        scores[ii] = np.sum(y_pred == y[test]) / float(len(y[test]))
        # feature_weights += feature_selection.inverse_transform(clf.coef_)

    print 'Average prediction accuracy: %0.3f | standard deviation:  %0.3f' % \
    (scores.mean(), scores.std())

# from sklearn import cross_validation
# from sklearn.feature_selection import SelectPercentile, f_classif



# loocv = cross_validation.LeaveOneOut(len(y))
# clf = RandomForestClassifier(n_estimators=500, max_features=np.sqrt(X.shape[1]), max_depth=None, min_samples_split=1, compute_importances=True)

# top_features = 50
# # computing feature importance
# acc = 0
# cnt = .0
# for train_index, test_index in loocv:
#     selector = SelectPercentile(f_classif, percentile=10)
#     selector.fit(X[train_index, :], y[train_index])
#     feature_scores = selector.scores_
#     indices = np.argsort(feature_scores)[::-1]

#     clf2 = RandomForestClassifier(n_estimators=500, max_features=np.sqrt(top_features), max_depth=None, min_samples_split=1)
#     best_features = X[:, indices[:top_features]]

#     for r in range(10):
#         clf2 = clf2.fit(best_features[train_index, :], y[train_index])
#         acc += clf2.score(best_features[test_index, :], y[test_index])
#         cnt += 1
# acc /= cnt


# # prepare feature weights for visualization
# feature_weights /= (ii + 1)  # create average weights
# # create mask to avoid division error
# feature_weights = np.ma.masked_array(feature_weights, feature_weights == 0)
# # normalize scores for visualization purposes
# feature_weights /= feature_weights.std(axis=1)[:, None]
# feature_weights -= feature_weights.mean(axis=1)[:, None]

# # unmask, take absolute values, emulate f-value scale
# feature_weights = np.abs(feature_weights.data) * 10

# vertices = [stc.lh_vertno, np.array([])]  # empty array for right hemisphere
# stc_feat = mne.SourceEstimate(feature_weights, vertices=vertices,
#             tmin=stc.tmin, tstep=stc.tstep,
#             subject='sample')

# brain = stc_feat.plot(subject=subject, fmin=1, fmid=5.5, fmax=20)
# brain.set_time(100)
# brain.show_view('l')
'''