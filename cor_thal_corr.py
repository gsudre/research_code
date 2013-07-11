import numpy as np
import env
import scipy
from scipy import stats

cortex = np.genfromtxt(env.data + '/structural/cortexR_SA_NV_10to21_2closestTo16.csv', delimiter=',')
# removing first column and first row, because they're headers
cortex = scipy.delete(cortex, 0, 1)
cortex = scipy.delete(cortex, 0, 0)
# format it to be subjects x variables
cortex = cortex.T

subcortex = np.genfromtxt(env.data + '/structural/thalamusR_SA_NV_10to21_2closestTo16.csv', delimiter=',')
# removing first column and first row, because they're headers
subcortex = scipy.delete(subcortex, 0, 1)
subcortex = scipy.delete(subcortex, 0, 0)
# format it to be subjects x variables
subcortex = subcortex.T

# selecting only a few vertices in the thalamus
# my_sub_vertices = [2310, 1574, 1692, 1262, 1350]
# my_sub_vertices = [1533, 1106, 225, 163, 2420, 2966, 1393, 1666, 1681, 1834, 2067]  # GS made it up by looking at anamoty, refer to Evernote for details
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


np.savez(env.results + 'structurals_pearson_all_thalamus_all_cortex_2closestTo16', corr=corr, pvals=pvals, my_sub_vertices=my_sub_vertices)
