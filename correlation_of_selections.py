''' Checks the correlation of two subject criteria '''
import numpy as np
import env
import scipy
from scipy import stats


def p(m):
    fig = ml.figure()
    brain  = surfer.Brain('mni','rh','cortex', curv=False, figure=fig)
    brain.add_data(m[:,v])


fname1 = env.data + '/structural/thalamusR_SA_NV_10to21_2closestTo16.csv'
fname2 = env.data + '/structural/thalamusR_SA_NV_10to21.csv'

cortex = np.genfromtxt(fname1, delimiter=',')
# removing first column and first row, because they're headers
cortex = scipy.delete(cortex, 0, 1)
cortex = scipy.delete(cortex, 0, 0)
# format it to be subjects x variables
cortex = cortex.T
c_names = np.recfromtxt(fname1, delimiter=',')[0][1:]

cortex2 = np.genfromtxt(fname2, delimiter=',')
# removing first column and first row, because they're headers
cortex2 = scipy.delete(cortex2, 0, 1)
cortex2 = scipy.delete(cortex2, 0, 0)
# format it to be subjects x variables
cortex2 = cortex2.T
c2_names = np.recfromtxt(fname2, delimiter=',')[0][1:]

# we have a different number of subjects in the two files, so let's crop the extra subjects in the bigger file to fit the smaller one
nvoxels = cortex.shape[1]

# we'll assume that cortex has more subjects than cortex2
if cortex.shape[0] < cortex2.shape[0]:
    tmp = cortex.copy()
    cortex = cortex2.copy()
    cortex2 = tmp

    tmp = c_names.copy()
    c_names = c2_names.copy()
    c2_names = tmp

# select what names need to be removed
rm_me = []
for i, name in enumerate(c_names):
    match = [m for m in c2_names if name == m]
    if len(match) == 0:
        rm_me.append(i)
cortex = scipy.delete(cortex, rm_me, 0)

# in the end we want to have one map over the brain, where the colors represent the correlation of that voxel with itself, using a different selection criteria.
corr = np.empty([nvoxels])
for v in range(nvoxels):
    corr[v] = stats.pearsonr(cortex[:, v], cortex2[:, v])[0]
