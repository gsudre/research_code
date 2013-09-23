import numpy as np
import os


def PLSC(X, Y, groups, num_comps=0):
    ''' Returns results of Partial Least Squares Correlation. groups is a list of 2-index lists, such as [[0, 10]] '''

    num_groups = len(groups)
    if Y.ndim == 1:
        num_seeds = 1
    else:
        num_seeds = Y.shape[1]

    # first, center and normalize matrices within groups. We remove the mean of each column, and then normalize it so that the sum squared of a column equals to 1.
    Xn = np.empty_like(X)
    Yn = np.empty_like(Y)
    for g in groups:
        Xg = X[g[0]:g[1], :]
        if Y.ndim > 1:
            Yg = Y[g[0]:g[1], :]
        else:
            Yg = Y[g[0]:g[1]]

        Xc = Xg - np.mean(Xg, axis=0)
        SSx = np.sum(Xc ** 2, axis=0)
        # make sure we don't divide by 0
        SSx[SSx == 0] = 1e-16
        # returning to the same sign as centered version, which gets lost after squaring
        signs = np.sign(Xc)
        signs[signs == 0] = 1
        Xn[g[0]:g[1], :] = signs * np.sqrt(Xc ** 2 / SSx)

        Yc = Yg - np.mean(Yg, axis=0)
        SSy = np.sum(Yc ** 2, axis=0)
        # SSy[SSy == 0] = 1e-16
        signs = np.sign(Yc)
        signs[signs == 0] = 1
        if Y.ndim > 1:
            Yn[g[0]:g[1], :] = signs * np.sqrt(Yc ** 2 / SSy)
        else:
            Yn[g[0]:g[1]] = signs * np.sqrt(Yc ** 2 / SSy)

    # now, compute the correlation matrix within groups
    R = np.zeros([num_seeds * num_groups, Xn.shape[1]])
    cnt = 0
    for g in groups:
        Xg = Xn[g[0]:g[1], :]
        if Y.ndim > 1:
            Yg = Yn[g[0]:g[1], :]
        else:
            Yg = Yn[g[0]:g[1]]

        R[cnt:(cnt + num_seeds), :] = np.dot(Yg.T, Xg)
        cnt += num_seeds

    # now we run SVD on the correlation matrix
    U, S, Vh = np.linalg.svd(R, full_matrices=False)
    V = Vh.T

    if num_comps <= 0:
        return S, V, U
    else:
        return S[:num_comps], V[:, :num_comps], U[:, :num_comps]


def load_structural(fname, groups, visit):
    csv = np.recfromtxt(fname, delimiter=',')
    labels = list(csv[0][3:])
    data = []
    group_names = []
    group_idx = []
    for row in csv[1:]:
        if row[1]==visit and row[2] in groups:
            data.append(list(row[3:].astype(np.float)))
            group_names.append(row[2])
    for group in groups:
         idx = [group_names.index(group), np.max(np.nonzero(np.array(group_names)==group)[0])+1]
         group_idx.append(idx)
    return np.array(data), labels, group_idx


# number of permutations/bootstraps to run
num_perms = 1000
groups = ['persistent', 'remission', 'NV']
brain = ['thalamus', 'striatum']
hemi = 'R'
visit = 'baseline'

# both X and Y are subjects x ROIs
X, rois0, group_idx = load_structural('%s/data/structural/rois_%s%s.csv' % (os.path.expanduser('~'), brain[0], hemi), groups, visit)
Y, rois1, group_idx = load_structural('%s/data/structural/rois_%s%s.csv' % (os.path.expanduser('~'), brain[1], hemi), groups, visit)

num_subjects = X.shape[0]

''' saliences is Xrois x LVs, and patterns is groups*Yrois x LVs, in the order
   YroisGrop1, YroisGroup2, ... '''
sv, saliences, patterns = PLSC(X, Y, group_idx)

num_comps = len(sv)

# calculating permutations to assess significance of SVs
saliences_perm = np.empty([saliences.shape[0], saliences.shape[1], num_perms])
patterns_perm = np.empty([patterns.shape[0], patterns.shape[1], num_perms])
sv_perm = np.empty([num_comps, num_perms])
for p in range(num_perms):
    print 'Permutation: ' + str(p+1) + '/' + str(num_perms)
    rand_indexes = np.random.permutation(num_subjects)
    Xp = X[rand_indexes, :]
    sv_perm[:, p], saliences_perm[:, :, p], patterns_perm[:, :, p] = PLSC(Xp, Y, group_idx, num_comps)

# calculating bootstraps to assess reliability of SVs
saliences_boot = np.empty([saliences.shape[0], saliences.shape[1], num_perms])
patterns_boot = np.empty([patterns.shape[0], patterns.shape[1], num_perms])
sv_boot = np.empty([num_comps, num_perms])
for p in range(num_perms):
    print 'Bootstrap: ' + str(p+1) + '/' + str(num_perms)
    rand_indexes = np.random.randint(num_subjects, size=num_subjects)
    # now we need to shuffle both X and Y, because we need to keep the relationships between observations
    Xb = X[rand_indexes, :]
    Yb = Y[rand_indexes, :]
    sv_boot[:, p], saliences_boot[:, :, p], patterns_boot[:, :, p] = PLSC(Xb, Yb, group_idx)

execfile("/Users/sudregp/research_code/correlation_analysis/analyze_PLSC_rois.py")

import matplotlib.pyplot as plt
lv=0
plt.figure()
ax = plt.subplot(111)

colors = ['red','orange','yellow','green','cyan', 'blue', 'purple', 'white', 'black', 'grey', 'brown']
rects = []
cnt = 0
Yrois = Y.shape[1]
for g in range(len(groups)):
    for i in range(cnt, Yrois*(g+1)):
        rects.append(plt.bar(i+g, patterns[i, lv], color=colors[i-cnt], label=rois1[i-cnt]))
    cnt += Yrois
plt.ylim([-1, 1])

# Shink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

# Put a legend to the right of the current axis
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.title(','.join(groups))

plt.figure()
ax = plt.subplot(111)

rects2 = []
cnt = 0
Xrois = X.shape[1]
for i in range(Xrois):
    rects2.append(plt.bar(i+g, stable_saliences[i, lv], color=colors[i-cnt], label=rois0[i-cnt]))
plt.ylim([-1, 1])

# Shink current axis by 20%
box = ax.get_position()
ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

# Put a legend to the right of the current axis
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
plt.title(brain[0])

plt.show(block=False)
