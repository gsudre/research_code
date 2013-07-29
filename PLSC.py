import numpy as np
import env
import scipy
import mne
import surfer
from mayavi import mlab
import glob


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

'''
 # Toy examples

X = np.array(
    [[5., 6, 1, 9, 1, 7, 6, 2, 1, 7],
    [1, 5, 8, 8, 7, 2, 8, 6, 4, 8],
    [8, 7, 3, 7, 1, 7, 4, 5, 1, 4],
    [3, 7, 6, 1, 1, 10, 2, 2, 1, 7],
    [3, 8, 7, 1, 6, 9, 1, 8, 8, 1],
    [7, 3, 1, 1, 3, 1, 8, 1, 3, 9],
    [0, 7, 1, 8, 7, 4, 2, 3, 6, 2],
    [0, 6, 5, 9, 7, 4, 4, 2, 10, 3],
    [7, 4, 5, 7, 6, 7, 6, 5, 4, 8]])

Y = np.array(
    [[2., 3],
    [4, 2],
    [5, 3],
    [3, 4],
    [2, 6],
    [1, 5],
    [9, 7],
    [8, 8],
    [7, 8]])

groups = [[0, 3], [3, 6], [6, 9]]
'''

# number of components to extract. Because we're only using seeds with one dimension, the econ version of svd only outputs one component!
# max_comps = 100

# number of permutations/bootstraps to run
num_perms = 200


cortex = np.genfromtxt(env.data + '/structural/cortexR_SA_NV_10to21_MATCH3.csv', delimiter=',')
# removing first column and first row, because they're headers
cortex = scipy.delete(cortex, 0, 1)
cortex = scipy.delete(cortex, 0, 0)
# format it to be subjects x variables
cortex = cortex.T

subcortex = np.genfromtxt(env.data + '/structural/thalamusR_SA_NV_10to21_MATCH3.csv', delimiter=',')
# removing first column and first row, because they're headers
subcortex = scipy.delete(subcortex, 0, 1)
subcortex = scipy.delete(subcortex, 0, 0)
# format it to be subjects x variables
subcortex = subcortex.T

# ADHD data
cortex2 = np.genfromtxt(env.data + '/structural/cortexR_SA_ADHD_10to21_MATCH3.csv', delimiter=',')
# removing first column and first row, because they're headers
cortex2 = scipy.delete(cortex2, 0, 1)
cortex2 = scipy.delete(cortex2, 0, 0)
# format it to be subjects x variables
cortex2 = cortex2.T

subcortex2 = np.genfromtxt(env.data + '/structural/thalamusR_SA_ADHD_10to21_MATCH3.csv', delimiter=',')
# removing first column and first row, because they're headers
subcortex2 = scipy.delete(subcortex2, 0, 1)
subcortex2 = scipy.delete(subcortex2, 0, 0)
# format it to be subjects x variables
subcortex2 = subcortex2.T

# selecting only a few vertices in the thalamus
# my_sub_vertices = [2310, 1574, 1692, 1262, 1350]  # Philip's
# my_sub_vertices = range(0, subcortex.shape[1], 100)  # every 100
# my_sub_vertices = range(subcortex.shape[1])
w = mne.read_w(env.fsl + '/mni/bem/cortex-3-rh.w')
my_cor_vertices = w['vertices']
# w = mne.read_w(env.fsl + '/mni/bem/thalamus-10-rh.w')
# my_sub_vertices = w['vertices']
# my_cor_vertices = range(cortex.shape[1])
# my_sub_vertices = [2034,  950,  216,   52, 2276, 2893, 1386, 1922, 2187, 1831, 1828]  # GS made it up by looking at anamoty, refer to Evernote for details. WRONG!
#my_sub_vertices = [1533, 1106, 225, 163, 2420, 2966, 1393, 1666, 1681, 1834, 2067]  # GS made it up by looking at anamoty, refer to Evernote for details
my_sub_vertices = []
# in nice order from anterior to posterior in the cortex (cingulate is last)
label_names = ['medialdorsal', 'va', 'vl', 'vp', 'lateraldorsal',
               'lateralposterior', 'pulvinar', 'anteriornuclei']
label_names = ['medialdorsal', 'va', 'vl', 'vp', 'pulvinar', 'anteriornuclei']
for l in label_names:
    v = mne.read_label(env.fsl + '/mni/label/rh.' + l + '.label')
    my_sub_vertices.append(v.vertices)

X = cortex[:, my_cor_vertices]
num_subjects = X.shape[0]
groups = [[0, num_subjects]]
#Y = subcortex[:, my_sub_vertices]
Y = np.zeros([num_subjects, len(my_sub_vertices)])
for r, roi in enumerate(my_sub_vertices):
    Y[:, r] = scipy.stats.nanmean(subcortex[:, roi], axis=1)

# Adding ADHDs
X = np.concatenate([X, cortex2[:, my_cor_vertices]], 0)
Ya = np.zeros([cortex2.shape[0], len(my_sub_vertices)])
for r, roi in enumerate(my_sub_vertices):
    Ya[:, r] = scipy.stats.nanmean(subcortex2[:, roi], axis=1)
Y = np.concatenate([Y, Ya], 0)
groups.append([num_subjects, X.shape[0]])
num_subjects = X.shape[0]

sv, saliences, patterns = PLSC(X, Y, groups)

num_comps = len(sv)

# calculating permutations to assess significance of SVs
saliences_perm = np.empty([saliences.shape[0], saliences.shape[1], num_perms])
patterns_perm = np.empty([patterns.shape[0], patterns.shape[1], num_perms])
sv_perm = np.empty([num_comps, num_perms])
for p in range(num_perms):
    print 'Permutation: ' + str(p+1) + '/' + str(num_perms)
    rand_indexes = np.random.permutation(num_subjects)
    Xp = X[rand_indexes, :]
    sv_perm[:, p], saliences_perm[:, :, p], patterns_perm[:, :, p] = PLSC(Xp, Y, groups, num_comps=num_comps)

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
    sv_boot[:, p], saliences_boot[:, :, p], patterns_boot[:, :, p] = PLSC(Xb, Yb, groups, num_comps=num_comps)


def plot_lv(lv):
    import matplotlib.pyplot as plt

    fig1 = mlab.figure()
    cor = surfer.Brain('mni', 'rh', 'cortex', curv=False, figure=fig1)
    cor.add_data(saliences[:, lv], vertices=my_cor_vertices)
    useTrans = len(my_cor_vertices) != saliences.shape[0]
    cor.scale_data_colormap(np.min(saliences[:, lv]), 0, np.max(saliences[:, lv]), useTrans)

    fig2 = mlab.figure()
    cor = surfer.Brain('mni', 'rh', 'cortex', curv=False, figure=fig2)
    cor.add_data(saliences[:, lv], vertices=my_cor_vertices)
    useTrans = len(my_cor_vertices) != saliences.shape[0]
    cor.scale_data_colormap(np.min(saliences[:, lv]), 0, np.max(saliences[:, lv]), useTrans)

    ind = np.arange(num_comps)    # the x locations for the groups
    width = 0.15       # the width of the bars: can also be len(x) sequence

    fig = plt.figure()
    ax = plt.subplot(111)

    # colors = ['r', 'g', 'b', 'y', 'k']
    from random import random
    colors = ['red','orange','yellow','green','cyan', 'blue', 'purple', 'white', 'black', 'grey', 'brown']
    # legend = ['mediodorsal', 'pulvinar', 'LGB', 'MGB', 'LP', 'LD', 'VPLc', 'VPL', 'VLO', 'VA', 'anterior']
    # colors = [(1,1,1)] + [(random(),random(),random()) for i in xrange(patterns.shape[0])]
    rects = [plt.bar(i, patterns[i, lv], color=colors[i], label=label_names[i]) for i in range(patterns.shape[0]/2)]
    rects = rects + [plt.bar(i+1, patterns[i, lv], color=colors[i-len(label_names)]) for i in range(len(label_names), patterns.shape[0])]
    # rects = []
    # for c, color in enumerate(colors):
    #     rects.append(pl.bar(ind + c * width, patterns[c, lv], width, color=color))

    # plt.ylabel('Saliences')
    # plt.title('Saliences by seed-voxel')
    # plt.xticks(ind + width / 2., ['LV' + str(i + 1) for i in range(num_comps)])
    # plt.plot(plt.xlim(), [0, 0], 'k')
    # plt.legend(rects, [str(i + 1) for i in my_sub_vertices], loc=0)

    # Shink current axis by 20%
    box = ax.get_position()
    ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])

    # Put a legend to the right of the current axis
    ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    # plt.legend(rects, legend, loc=0)

    plt.show(block=False)
    # fig2 = mlab.figure()
    # tha = surfer.Brain('mni', 'rh', 'thalamus', curv=False, figure=fig2)
    # tha.add_data(patterns[:, lv], vertices=my_sub_vertices, smoothing_steps=1)
    # tha.scale_data_colormap(np.min(patterns[:, lv]), 0, np.max(patterns[:, lv]), True)
