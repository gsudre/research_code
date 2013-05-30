import numpy as np
import env
import scipy
import pdb
import matplotlib.pyplot as plt
from scipy import stats
import procrustes


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


num_perms = sv_perm.shape[-1]

sv2 = np.tile(sv, (num_perms, 1)).T
tmp = sv_perm >= sv2
pvals = np.sum(tmp, axis=-1) / float(num_perms)

sem = scipy.stats.sem(saliences_boot, axis=-1)
stable_saliences = saliences / sem
sem = scipy.stats.sem(patterns_boot, axis=-1)
stable_patterns = patterns / sem

''' This is running quite slow...
# doing the same as above, but rotating the results first
saliences_boot_rot = np.empty_like(saliences_boot)
patterns_boot_rot = np.empty_like(patterns_boot)
for p in range(num_perms):
    print str(p+1) + '/' + str(num_perms)
    Vresamp = np.squeeze(saliences_boot[:, :, p])
    Uresamp = np.squeeze(patterns_boot[:, :, p])
    saliences_boot_rot[:, :, p] = procrustes.procrustes(saliences, Vresamp)[0]
    patterns_boot_rot[:, :, p] = procrustes.procrustes(patterns, Uresamp)[0]

sem = scipy.stats.sem(saliences_boot_rot, axis=-1)
stable_saliences_rot = saliences / sem
sem = scipy.stats.sem(patterns_boot_rot, axis=-1)
stable_patterns_rot = patterns / sem
'''
