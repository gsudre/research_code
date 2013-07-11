''' Predicts the rate of change in one group of voxels (e.g. thalamus) based on a different group (e.g. cortex). '''

import numpy as np
import env
import scipy
from scipy import stats
from sklearn import linear_model, cross_validation

# cortex = np.genfromtxt(env.data + '/structural/cortex_SA_NV_10to21.csv', delimiter=',')
# # removing first column and first row, because they're headers
# cortex = scipy.delete(cortex, 0, 1)
# cortex = scipy.delete(cortex, 0, 0)
# # format it to be subjects x variables
# cortex = cortex.T

# subcortex = np.genfromtxt(env.data + '/structural/thalamus_SA_NV_10to21.csv', delimiter=',')
# # removing first column and first row, because they're headers
# subcortex = scipy.delete(subcortex, 0, 1)
# subcortex = scipy.delete(subcortex, 0, 0)
# # format it to be subjects x variables
# subcortex = subcortex.T

Y = cortex
X = subcortex

alphas = np.logspace(-4, -.5, 20)

Xn = stats.mstats.zscore(X, axis=0)
y_voxels = range(0, Y.shape[1], 100)

lasso_cv = linear_model.LassoCV(alphas=alphas)
k_fold = cross_validation.KFold(Xn.shape[0], 10)
scores = np.zeros([len(k_fold), len(y_voxels)])
alphas = np.zeros([len(k_fold), len(y_voxels)])
for k, (train, test) in enumerate(k_fold):
    print 'fold {%d}' % k
    for v, voxel in enumerate(y_voxels):
        lasso_cv.fit(Xn[train, :], Y[train, voxel])
        scores[k, v] = lasso_cv.score(Xn[test, :], Y[test, voxel])
        alphas[k, v] = lasso_cv.alpha_
