import numpy as np
import env
import scipy
import pdb
from scipy import stats

# number of components to extract. Because we're only using seeds with one dimension, the econ version of svd only outputs one component!
max_comps = 5
# selecting only a few vertices in the thalamus
my_sub_vertices = [2310, 1574, 1692, 1262, 1350]
# number of permutations/bootstraps to run
num_perms = 1000

cortex = np.genfromtxt(env.data + '/structural/slopes_nv_284.csv', delimiter=',')
# removing first 2 columns and first row, because they're headers
cortex = scipy.delete(cortex, [0, 1], 1)
cortex = scipy.delete(cortex, 0, 0)
# format it to be subjects x variables
cortex = cortex.T

subcortex = np.genfromtxt(env.data + '/structural/THALAMUS_284_slopes.csv', delimiter=',')
# removing first 2 columns and first row, because they're headers
subcortex = scipy.delete(subcortex, [0, 1], 1)
subcortex = scipy.delete(subcortex, 0, 0)
# format it to be subjects x variables
subcortex = subcortex.T

my_sub_vertices = range(subcortex.shape[1])
num_subjects = cortex.shape[0]

X = cortex
Y = subcortex[:, my_sub_vertices]
corr = np.empty([X.shape[1], Y.shape[1]])
pvals = np.empty([X.shape[1], Y.shape[1]])
for x in range(X.shape[1]):
    print str(x+1) + '/' + str(X.shape[1])
    for y in range(Y.shape[1]):
        corr[x, y], pvals[x, y] = stats.pearsonr(X[:, x], Y[:, y])


np.savez(env.results + 'structurals_pearson_all_thalamus_all_cortex', corr=corr, pvals=pvals, my_sub_vertices=my_sub_vertices)
