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

Y = cortex

alphas = np.logspace(-4, -.5, 20)

y_voxels = range(0, Y.shape[1], 100)

my_sub_vertices = []
# in nice order from anterior to posterior in the cortex (cingulate is last)
label_names = ['medialdorsal', 'va', 'vl', 'vp', 'lateraldorsal',
               'lateralposterior', 'pulvinar', 'anteriornuclei']
label_names = ['medialdorsal', 'va', 'vl', 'vp', 'pulvinar', 'anteriornuclei']
for l in label_names:
    v = mne.read_label(env.fsl + '/mni/label/rh.' + l + '.label')
    my_sub_vertices.append(v.vertices)

num_subjects = cortex.shape[0]


X = np.zeros([num_subjects, len(my_sub_vertices)])
for r, roi in enumerate(my_sub_vertices):
    X[:, r] = scipy.stats.nanmean(subcortex[:, roi], axis=1)


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

forest = ensemble.ExtraTreesRegressor(n_estimators=10,
                             max_features=X.shape[1],
                             random_state=0)
k_fold = cross_validation.KFold(X.shape[0], 10)
scores = np.zeros([len(k_fold), len(y_voxels)])
for k, (train, test) in enumerate(k_fold):
    for v, y in enumerate(y_voxels):
        forest.fit(X[train,:], Y[train,y])
        scores[k, v] = forest.score(X[test,:], Y[test,y])
        print '%.3f' % scores[k,v]

# offset = int(X.shape[0] * 0.9)
# X_train, y_train = X[:offset], Y[:offset]
# X_test, y_test = X[offset:], Y[offset:]
# params = {'n_estimators': 500, 'max_depth': 4, 'min_samples_split': 1,
#           'learning_rate': 0.001, 'loss': 'ls', 'max_features': 100}
# clf = ensemble.GradientBoostingRegressor(**params)
# yv = 100
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
# pl.show()

# feature_importance = clf.feature_importances_
# # make importances relative to max importance
# feature_importance = 100.0 * (feature_importance / feature_importance.max())
# sorted_idx = np.argsort(feature_importance)
# pos = np.arange(10) + .5  #sorted_idx[:10].shape[0]) + .5
# pl.subplot(1, 2, 2)
# pl.barh(pos, feature_importance[sorted_idx[:10]], align='center')
# # pl.yticks(pos, boston.feature_names[sorted_idx[:10]])
# pl.xlabel('Relative Importance')
# pl.title('Variable Importance')
# pl.show()
# from sklearn.cross_validation import cross_val_score
# from sklearn.ensemble import RandomForestRegressor
# yv = 0
# clf = RandomForestRegressor(n_estimators=10, max_depth=None, min_samples_split=1, random_state=0)
# scores = cross_val_score(clf, X, Y[:, yv])
# scores.mean()  
