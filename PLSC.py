import numpy as np
import env
import scipy


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


''' # Toy examples

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

# selecting only a few vertices in the thalamus
my_sub_vertices = [2310, 1574, 1692, 1262, 1350]
# my_sub_vertices = range(0, subcortex.shape[1], 100)

num_subjects = cortex.shape[0]

X = cortex
groups = [[0, num_subjects]]
Y = subcortex[:, my_sub_vertices]

sv, saliences, patterns = PLSC(X, Y, groups)

'''
num_comps = len(sv)

# calculating permutations to assess significance of SVs
sv_perm = np.empty([num_comps, num_perms])
for p in range(num_perms):
    print 'Permutation: ' + str(p+1) + '/' + str(num_perms)
    rand_indexes = np.random.permutation(num_subjects)
    Xp = X[rand_indexes, :]
    sv_perm[:, p], _, _ = PLSC(Xp, Y, groups, num_comps=num_comps)

# calculating bootstraps to assess reliability of SVs
saliences_boot = np.empty([X.shape[1], num_comps, num_perms])
patterns_boot = np.empty([Y.shape[1], num_comps, num_perms])
for p in range(num_perms):
    print 'Bootstrap: ' + str(p+1) + '/' + str(num_perms)
    rand_indexes = np.random.randint(num_subjects, size=num_subjects)
    # now we need to shuffle both X and Y, because we need to keep the relationships between observations
    Xb = X[rand_indexes, :]
    Yb = Y[rand_indexes, :]
    _, saliences_boot[:, :, p], patterns_boot[:, :, p] = PLSC(Xb, Yb, groups, num_comps=num_comps)

np.savez(env.results + 'structurals_seedPLS_5_thalamus_all_cortex', sv_perm=sv_perm, saliences_boot=saliences_boot, patterns_boot=patterns_boot, sv=sv, saliences=saliences, patterns=patterns, my_sub_vertices=my_sub_vertices)
'''
