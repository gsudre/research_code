# combines the results of permuting roi correlations
import numpy as np
import glob
import os


group_data = np.load(os.path.expanduser('~') + '/data/results/structural/pearson_rois_thalamus_striatum_baseAndLast18_NVvsADHD.npz')

# we structured it so that G1 is hypothesized to be bigger than G2
D = group_data['diff_last_base_G1'] - group_data['diff_last_base_G2']

# check how often the permuted differences were as big as the real difference
pvals = np.zeros_like(D)
perm_files = glob.glob(os.path.expanduser('~') + '/data/results/structural/perms/pearson_rois_thalamus_striatum_baseAndLast18_NVvsADHD_perm*.npz')
for file in perm_files:
    res = np.load(file)
    permD = res['diff_last_base_G1'] - res['diff_last_base_G2']
    # permD has a distribution for each vertex combination, so we test against the max of the distribtuion (i.e. the biggest difference by chance)
    maxPermD = np.max(permD,axis=-1)
    bad_Ds = maxPermD >= D
    pvals[bad_Ds] += 1
pvals /= len(perm_files)
