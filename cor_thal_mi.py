# Computes the mutual information among vertices of different matrices
import numpy as np
import env
import scipy
import entropy_estimators as ee
import mne
import glob

cortex = np.genfromtxt('/Users/sudregp/Documents/surfaces/baseline_striatumR_SA_NV_QCCIVETlt35_QCSUBePASS.csv', delimiter=',')
# removing first column and first row, because they're headers
cortex = scipy.delete(cortex, 0, 1)
cortex = scipy.delete(cortex, 0, 0)
# format it to be subjects x variables
cortex = cortex.T

subcortex = np.genfromtxt('/Users/sudregp/Documents/surfaces/baseline_thalamusR_SA_NV_QCCIVETlt35_QCSUBePASS.csv', delimiter=',')
# removing first column and first row, because they're headers
subcortex = scipy.delete(subcortex, 0, 1)
subcortex = scipy.delete(subcortex, 0, 0)
# format it to be subjects x variables
subcortex = subcortex.T

# selecting only a few vertices in the thalamus
my_sub_vertices = range(subcortex.shape[1])

num_subjects = cortex.shape[0]

X = cortex

Y = subcortex[:, my_sub_vertices]

MI = np.empty([X.shape[1], Y.shape[1]])
for x in range(X.shape[1]):
    print str(x+1) + '/' + str(X.shape[1])
    Xv = [[i] for i in X[:, x]]
    for y in range(Y.shape[1]):
        Yv = [[i] for i in Y[:, y]]
        MI[x, y] = ee.mi(Xv,Yv)


np.savez(env.results + 'structurals_mi_thalamus_striatum_NV_QCCIVETlt35_QCSUBePASS', MI=MI)
