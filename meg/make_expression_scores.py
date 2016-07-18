# Generates expression scores for all subjects given a band and method
import tables
import numpy as np
import sys
import statsmodels.formula.api as smf


band = sys.argv[1]
method = sys.argv[2]
fname = '/data/NCR_SBRB/ica_results_%s_%s_enriched_50perms_15ics.mat' % (band, method)
file = tables.openFile(fname)
S = file.root.S[:]
fname = '/data/NCR_SBRB/ica_results_%s_%s_enrichedYddOnly.mat' % (band, method)
file = tables.openFile(fname)
res_mats = file.root.Ydd[:].T
scores = []
for s in range(res_mats.shape[0]):
    print s
    est = smf.OLS(res_mats[s, :], S).fit()
    scores.append(est.params)
exp_scores = np.array(scores)
fname = '/data/NCR_SBRB/exp_scores_%s_%s_enriched_50perms_15ics.npy' % (band, method)
np.save(fname, exp_scores)
