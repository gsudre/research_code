import numpy as np
import env
import scipy
import pdb


def procrustes(Vorig, Vresamp, Sresamp):
    ''' Following the algorithm in McIntosh and Lobaugh, 2004 ''' 
    N, O, Ph = np.linalg.svd(np.dot(Vorig.T, Vresamp), full_matrices=False)
    P = Ph.T

    Q = np.dot(N, P.T)
    if Sresamp.ndim == 1:
        Sresamp = Sresamp * np.eye(len(Sresamp))

    Vhat = np.dot(Vresamp, np.dot(Sresamp, Q))
    Shat = np.sqrt(np.sum(Vhat ** 2, axis=0))

    return Vhat, Shat


num_perms = sv_perm.shape[-1]

sv2 = np.tile(sv, (1, 1, num_perms))
sv2 = sv2.transpose([1, 0, 2])
tmp = sv_perm >= sv2
pvals = np.sum(tmp, axis=-1) / float(num_perms)

sem = scipy.stats.sem(saliences_boot, axis=-1)
stable = saliences / sem

# doing the same as above, but rotating the results first
sv_perm_rot = np.empty_like(sv_perm)
saliences_boot_rot = np.empty_like(saliences_boot)
for y in range(saliences_boot.shape[0]):
    print str(y+1) + '/' + str(saliences_boot.shape[0])
    Vorig = np.tile(np.squeeze(saliences[y, :, :]), [1, 1]).T
    for p in range(num_perms):
        Vresamp = np.tile(np.squeeze(saliences_boot[y, :, :, p]), [1, 1]).T
        Sresamp = sv_perm[y, :, p]
        saliences_boot_rot[y, :, :, p], sv_perm_rot[y, :, p] = procrustes(Vorig, Vresamp, Sresamp)

tmp = sv_perm_rot >= sv2
pvals_rot = np.sum(tmp, axis=-1) / float(num_perms)

sem = scipy.stats.sem(saliences_boot_rot, axis=-1)
stable_rot = saliences / sem
