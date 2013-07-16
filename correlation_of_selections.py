''' Checks the correlation of two subject criteria '''
import numpy as np
import env
import scipy
from scipy import stats

cortex = np.genfromtxt(env.data + '/structural/cortexR_SA_NV_10to21_3orMore.csv', delimiter=',')
# removing first column and first row, because they're headers
cortex = scipy.delete(cortex, 0, 1)
cortex = scipy.delete(cortex, 0, 0)
# format it to be subjects x variables
cortex = cortex.T

cortex2 = np.genfromtxt(env.data + '/structural/cortex_SA_NV_10to21.csv', delimiter=',')
# removing first column and first row, because they're headers
cortex2 = scipy.delete(cortex2, 0, 1)
cortex2 = scipy.delete(cortex2, 0, 0)
# format it to be subjects x variables
cortex2 = cortex2.T

# we have a different number of subjects in the two files, so let's sample the number with more subjects a few times before computing this
nperms = 100
nvoxels = cortex.shape[1]

# we'll assume that cortex has more subjects than cortex2
if cortex.shape[0] < cortex2.shape[0]:
    tmp = cortex.copy()
    cortex = cortex2.copy()
    cortex2 = tmp

# in the end we want to have one map over the brain, where the colors represent the correlation of that voxel with itself, using a different selection criteria.
corr = np.empty([nvoxels])
for v in range(nvoxels):
    print 'voxel', v
    tmp_corr = []
    for p in range(nperms):
        index = np.random.permutation(cortex.shape[0])[:cortex2.shape[0]]
        tmp_corr.append(stats.pearsonr(cortex[index, v], cortex2[:, v])[0])
    corr[v] = np.mean(tmp_corr)
