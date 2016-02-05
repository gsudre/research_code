''' Checks whether there is a group difference in the correlation map for a given seed '''

import mne
import numpy as np

seed_src = 11543
bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
subjs_fname = '/Users/sudregp/data/meg/good_subjects.txt'
nvs_fname = '/Users/sudregp/data/meg/nv_subjs.txt'
adhds_fname = '/Users/sudregp/data/meg/adhd_subjs.txt'
persistent_fname = '/Users/sudregp/data/meg/persistent_pm2std.txt'
remitted_fname = '/Users/sudregp/data/meg/remitted_pm2std.txt'
data_dir = '/Users/sudregp/data/results/meg/'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
nfid = open(nvs_fname, 'r')
afid = open(adhds_fname, 'r')
pfid = open(persistent_fname, 'r')
rfid = open(remitted_fname, 'r')
adhd = [line.rstrip() for line in afid]
nv = [line.rstrip() for line in nfid]
per = [line.rstrip() for line in pfid]
rem = [line.rstrip() for line in rfid]

for band in bands:
    print band
    # load the pre-computed correlation data
    fname = data_dir + 'corrs-seed%d-%dto%d-lh.stc'%(seed_src,band[0],band[1])
    stc = mne.read_source_estimate(fname)

    # Make arrays X and y such that :
    # X is 2d with X.shape[0] is the total number of epochs to classify
    # y is filled with integers coding for the class to predict
    # We must have X.shape[0] equal to y.shape[0]
    X = []
    y = []
    subj_names = []
    cnt = 0
    for s in subjs:
        if s in nv:
            y.append(1)
            subj_names.append(s)
            X.append(stc.data[:,cnt].T)
        elif s in adhd:
            y.append(0)
            subj_names.append(s)
            X.append(stc.data[:,cnt].T)
        cnt+=1
    y = np.asarray(y).T
    X = np.asarray(X)
    Xorig = X.copy()

    # we have to normalize the data before supplying them to our classifier
    X -= X.mean(axis=0)
    X /= X.std(axis=0)
    # replace the seed feature by a constant random value so we cannot use it for classification, but it doesn't become a NaN after normalization
    X[:,seed_src] = np.random.randn(1)[0]

    # prepare classifier
    from sklearn.svm import SVC, LinearSVC
    from sklearn.cross_validation import ShuffleSplit, LeaveOneOut
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.feature_selection import SelectKBest, f_classif

    # Define a monte-carlo cross-validation generator (reduce variance):
    n_splits = 10
    clf = SVC(C=1, kernel='linear')
    cv = ShuffleSplit(len(X), n_splits, test_size=0.2)
    # cv = LeaveOneOut(X.shape[0])

    from sklearn.pipeline import Pipeline


    # initialize score and feature weights result arrays
    n_feats = X.shape[1]
    scores = np.zeros(len(cv))
    # scores = np.zeros(X.shape[0])
    feature_weights = np.zeros([1, n_feats])

    # # clf = Pipeline([
    # #   ('feature_selection', LinearSVC(penalty="l1",dual=False)),
    # #   ('classification', LinearSVC(penalty='l2'))
    # # ])
    # # clf.fit(X, y)

    feature_selection = SelectKBest(f_classif, k=50)  # take the best 500
    # to make life easier we will create a pipeline object
    pipe = Pipeline([('anova', feature_selection), ('svc', clf)])

    # where the magic happens
    for ii, (train, test) in enumerate(cv):
        pipe.fit(X[train], y[train])
        y_pred = pipe.predict(X[test])
        scores[ii] = np.sum(y_pred == y[test]) / float(len(y[test]))
        feature_weights += feature_selection.inverse_transform(clf.coef_)

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
