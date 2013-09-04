import numpy as np
import env
import scipy
from scipy import stats

fname = 'structurals_pearson_thalamus_striatum_ADHD_QCCIVETlt35_QCSUBePASS_boot%04d' % np.random.randint(9999)
cortex = np.genfromtxt('/Users/sudregp/Documents/surfaces/baseline_striatumR_SA_ADHD_QCCIVETlt35_QCSUBePASS.csv', delimiter=',')
# removing first column and first row, because they're headers
cortex = scipy.delete(cortex, 0, 1)
cortex = scipy.delete(cortex, 0, 0)
# format it to be subjects x variables
cortex = cortex.T

subcortex = np.genfromtxt('/Users/sudregp/Documents/surfaces/baseline_thalamusR_SA_ADHD_QCCIVETlt35_QCSUBePASS.csv', delimiter=',')
# removing first column and first row, because they're headers
subcortex = scipy.delete(subcortex, 0, 1)
subcortex = scipy.delete(subcortex, 0, 0)
# format it to be subjects x variables
subcortex = subcortex.T

num_subjects = cortex.shape[0]
boot_idx = np.random.random_integers(0, num_subjects-1, num_subjects)

X = cortex[boot_idx, :]
Y = subcortex[boot_idx, :]

corr = np.empty([X.shape[1], Y.shape[1]])
pvals = np.empty([X.shape[1], Y.shape[1]])
for x in range(X.shape[1]):
    print str(x+1) + '/' + str(X.shape[1])
    for y in range(Y.shape[1]):
        corr[x, y], pvals[x, y] = stats.pearsonr(X[:, x], Y[:, y])

np.savez(env.results + fname, corr=corr, pvals=pvals)
