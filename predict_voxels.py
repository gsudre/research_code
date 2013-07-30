''' Predicts the rate of change in one group of voxels (e.g. thalamus) based on a different group (e.g. cortex). '''

import numpy as np
import env
import scipy
from scipy import stats
from sklearn import linear_model, cross_validation, ensemble
from sklearn.metrics import mean_squared_error
import pylab as pl
import mne

# cortex = np.genfromtxt(env.data + '/structural/cortexR_SA_NV_10to21.csv', delimiter=',')
# # removing first column and first row, because they're headers
# cortex = scipy.delete(cortex, 0, 1)
# cortex = scipy.delete(cortex, 0, 0)
# # format it to be subjects x variables
# cortex = cortex.T

# subcortex = np.genfromtxt(env.data + '/structural/thalamusR_SA_NV_10to21.csv', delimiter=',')
# # removing first column and first row, because they're headers
# subcortex = scipy.delete(subcortex, 0, 1)
# subcortex = scipy.delete(subcortex, 0, 0)
# # format it to be subjects x variables
# subcortex = subcortex.T

# w = mne.read_w(env.fsl + '/mni/bem/cortex-3-rh.w')
# y_voxels = w['vertices']

Y = cortex[:, y_voxels]

alphas = np.logspace(-4, -.5, 20)

my_sub_vertices = []
# in nice order from anterior to posterior in the cortex (cingulate is last)
label_names = ['medialdorsal', 'va', 'vl', 'vp', 'lateraldorsal',
               'lateralposterior', 'pulvinar', 'anteriornuclei']
# label_names = ['medialdorsal', 'va', 'vl', 'vp', 'pulvinar', 'anteriornuclei']
for l in label_names:
    v = mne.read_label(env.fsl + '/mni/label/rh.' + l + '.label')
    my_sub_vertices.append(v.vertices)

num_subjects = cortex.shape[0]


# X = np.zeros([num_subjects, len(my_sub_vertices)])
# for r, roi in enumerate(my_sub_vertices):
#     X[:, r] = scipy.stats.nanmean(subcortex[:, roi], axis=1)
X = subcortex

# lasso_cv = linear_model.LassoCV(alphas=alphas)
# k_fold = cross_validation.KFold(X.shape[0], 10)
# scores = np.zeros([len(k_fold), len(y_voxels)])
# alphas = np.zeros([len(k_fold), len(y_voxels)])
# for k, (train, test) in enumerate(k_fold):
#     print 'fold {%d}' % k
#     for v, voxel in enumerate(y_voxels):
#         lasso_cv.fit(X[train, :], Y[train, voxel])
#         scores[k, v] = lasso_cv.score(X[test, :], Y[test, voxel])
#         alphas[k, v] = lasso_cv.alpha_

# from sklearn.tree import DecisionTreeRegressor
# forest = DecisionTreeRegressor(max_depth=Y.shape[1], compute_importances=True)
# k_fold = cross_validation.KFold(X.shape[0], 30)
# scores = np.zeros([len(k_fold), len(y_voxels)])
# for k, (train, test) in enumerate(k_fold):
#     forest.fit(X[train, :], Y[train, :])
#     y_pred = forest.predict(X[test, :])
#     for v in range(len(y_voxels)):
#         numerator = ((Y[test, v] - y_pred[:, v]) ** 2).sum()
#         denominator = ((Y[test, v] - Y[test, v].mean(axis=0)) ** 2).sum()
#         scores[k, v] = 1 - numerator/denominator
#         # print '%.3f' % scores[k, v]

k_fold = cross_validation.KFold(X.shape[0], 10)
params = {'n_estimators': 500, 'max_depth': 4, 'learning_rate': 0.01, 'loss': 'ls', 'subsample': .7}
clf = ensemble.GradientBoostingRegressor(**params)
cortex_voxels = range(0, Y.shape[1], 100)
cortex_voxels = [2500]
test_score = np.zeros((params['n_estimators'],), dtype=np.float64)
train_score = np.zeros((params['n_estimators'],), dtype=np.float64)
good_voxels = []
where = []
for yv in cortex_voxels:
    print yv
    for (train, test) in k_fold:
        X_train, y_train = X[train], Y[train, yv]
        X_test, y_test = X[test], Y[test, yv]
        clf.fit(X_train, y_train)
        train_score += clf.train_score_
        for i, y_pred in enumerate(clf.staged_decision_function(X_test)):
            test_score[i] += clf.loss_(y_test, y_pred)
    train_score /= k_fold.n_folds
    test_score /= k_fold.n_folds

    if np.argmin(test_score) > 0:
        good_voxels.append(yv)
        where.append(np.argmin(test_score))

pl.figure(figsize=(12, 6))
pl.title('Deviance')
pl.plot(np.arange(params['n_estimators']) + 1, train_score, 'b-',
        label='Training Set Deviance')
pl.plot(np.arange(params['n_estimators']) + 1, test_score, 'r-',
        label='Test Set Deviance')
pl.legend(loc='upper right')
pl.xlabel('Boosting Iterations')
pl.ylabel('Deviance')
pl.show(block=False)

# offset = int(X.shape[0] * 0.9)
# X_train, y_train = X[:offset], Y[:offset]
# X_test, y_test = X[offset:], Y[offset:]
# params = {'n_estimators': 500, 'max_depth': 4, 'min_samples_split': 1,
#           'learning_rate': 0.001, 'loss': 'ls', 'max_features': X.shape[1]}
# clf = ensemble.GradientBoostingRegressor(**params)
# yv = 10
# clf.fit(X_train, y_train[:, yv])
# mse = mean_squared_error(y_test[:, yv], clf.predict(X_test))
# print("MSE: %.4f" % mse)
# ###############################################################################
# # Plot training deviance

# # compute test set deviance
# test_score = np.zeros((params['n_estimators'],), dtype=np.float64)
# for i, y_pred in enumerate(clf.staged_decision_function(X_test)):
#     test_score[i] = clf.loss_(y_test[:, yv], y_pred)
# pl.figure(figsize=(12, 6))
# pl.subplot(1, 2, 1)
# pl.title('Deviance')
# pl.plot(np.arange(params['n_estimators']) + 1, clf.train_score_, 'b-',
#         label='Training Set Deviance')
# pl.plot(np.arange(params['n_estimators']) + 1, test_score, 'r-',
#         label='Test Set Deviance')
# pl.legend(loc='upper right')
# pl.xlabel('Boosting Iterations')
# pl.ylabel('Deviance')

# feature_importance = clf.feature_importances_
# # make importances relative to max importance
# feature_importance = 100.0 * (feature_importance / feature_importance.max())
# sorted_idx = np.argsort(feature_importance)
# pos = np.arange(sorted_idx.shape[0]) + .5
# pl.subplot(1, 2, 2)
# pl.barh(pos, feature_importance[sorted_idx], align='center')
# # pl.yticks(pos, boston.feature_names[sorted_idx])
# pl.xlabel('Relative Importance')
# pl.title('Variable Importance')
# pl.show(block=False)

# from sklearn.cross_validation import cross_val_score
# from sklearn.ensemble import RandomForestRegressor
# yv = 0
# clf = RandomForestRegressor(n_estimators=10, max_depth=None, min_samples_split=1, random_state=0)
# scores = cross_val_score(clf, X, Y[:, yv])
# scores.mean()  
