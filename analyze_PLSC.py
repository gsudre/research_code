import numpy as np
import env
import scipy
import matplotlib.pyplot as plt
from scipy import stats
import procrustes as pc
import pdb

'''
ind = np.arange(num_comps)    # the x locations for the groups
width = 0.15       # the width of the bars: can also be len(x) sequence

fig = plt.figure()

colors = ['r', 'g', 'b', 'y', 'k']
rects = []
for c, color in enumerate(colors):
    rects.append(plt.bar(ind + c * width, patterns[c, :], width, color=color))

plt.ylabel('Saliences')
plt.title('Saliences by seed-voxel')
plt.xticks(ind + width / 2., ['LV' + str(i + 1) for i in range(num_comps)])
plt.plot(plt.xlim(), [0, 0], 'k')
plt.legend(rects, [str(i + 1) for i in my_sub_vertices], loc=0)

plt.show(block=False)
'''


# def procrustes(Vorig, Vresamp, Uresamp, Sresamp):
#     ''' Following the algorithm in McIntosh and Lobaugh, 2004 ''' 
#     N, O, Ph = np.linalg.svd(np.dot(Vorig.T, Vresamp), full_matrices=False)
#     P = Ph.T

#     Q = np.dot(N, P)
#     if Sresamp.ndim == 1:
#         Sresamp = Sresamp * np.eye(len(Sresamp))

#     Vhat = np.dot(Vresamp, np.dot(Sresamp, Q))
#     Uhat = np.dot(Uresamp, np.dot(Sresamp, Q))
#     # Shat = np.sqrt(np.sum(Vhat ** 2, axis=0))
#     _, Shat, _= np.linalg.svd(Vhat, full_matrices=False)

#     return Vhat, Uhat, Shat


num_perms = saliences_boot.shape[-1]
sv2 = np.tile(sv, [num_perms, 1]).T

# rotate the matrices so we can compare permutted/bootstrap data and the original SVD space
for p in range(num_perms):
    print str(p+1) + '/' + str(num_perms)

    tmps = pc.procrustes(saliences.T, np.squeeze(saliences_boot[:, :, p]).T)
    std_salience = tmps[0].T
    saliences_boot[:, :, p] = tmps[1].T.copy()

    tmpp = pc.procrustes(patterns.T, np.squeeze(patterns_boot[:, :, p]).T)
    std_pattern = tmpp[0].T
    patterns_boot[:, :, p] = tmpp[1].T.copy()
std_saliences = tmps[0].T
std_patterns = tmpp[0].T

pvals = np.sum(sv_perm >= sv2, axis=-1) / float(num_perms)
se = np.std(saliences_boot, axis=-1)
stability_saliences = std_saliences / se
se = np.std(patterns_boot, axis=-1)
stability_patterns = std_patterns / se

# saliences and patterns with absolute value > 2.32 give p-value < .01, so we should only keep those. This is a way to do it:
stable_saliences = saliences.copy()
stable_saliences[np.abs(stability_saliences) <= 2.33] = 0
stable_patterns = patterns.copy()
stable_patterns[np.abs(stability_patterns) <= 2.33] = 0

# np.savez(env.results + 'structurals_seedPLS_5_thalamus_all_cortex', pvals=pvals, stability_saliences=stability_saliences, stability_patterns=stability_patterns, sv=sv, saliences=saliences, patterns=patterns, my_sub_vertices=my_sub_vertices)
