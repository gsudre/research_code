import numpy as np


def procrustes_rotation(Vorig, Vresamp):
    ''' Following the PLS for neuroimaging software code in rri_bootprocrust.m (research.baycrest.org/pls/) '''
    # pdb.set_trace()
    # define coordinate space between original and bootstratp VLs
    tmp = np.dot(Vorig.T, Vresamp)

    # orthogonalize space
    N, O, Ph = np.linalg.svd(tmp, full_matrices=True)
    P = Ph.T

    # determine procrustean transform
    rmat = np.dot(P, N.T)

    return rmat


num_perms = saliences_boot.shape[-1]

saliences_rot = np.empty_like(saliences_boot)
patterns_rot = np.empty_like(patterns_boot)
sv_rot = np.empty_like(sv_boot)

# rotate the matrices so we can compare bootstrap data and the original SVD space
for p in range(num_perms):
    print str(p+1) + '/' + str(num_perms)
    Q = procrustes_rotation(saliences, np.squeeze(saliences_boot[:, :, p]))
    saliences_rot[:, :, p] = np.dot(np.squeeze(saliences_boot[:, :, p]), np.dot(np.diag(sv_boot[:, p]), Q))
    patterns_rot[:, :, p] = np.dot(np.squeeze(patterns_boot[:, :, p]), np.dot(np.diag(sv_boot[:, p]), Q))

    Qperm = procrustes_rotation(saliences, np.squeeze(saliences_perm[:, :, p]))
    Vrot = np.dot(np.squeeze(saliences_perm[:, :, p]), np.dot(np.diag(sv_perm[:, p]), Qperm))
    sv_rot[:, p] = np.sqrt(np.sum(Vrot ** 2, axis=0))

sv2 = np.tile(sv, [num_perms, 1]).T
pvals = np.sum(sv_rot >= sv2, axis=-1) / float(num_perms)
se = np.std(saliences_rot, axis=-1)
stability_saliences = saliences / se
se = np.std(patterns_rot, axis=-1)
stability_patterns = patterns / se

# saliences and patterns with absolute value > 2.32 give p-value < .01, and 1.96 for p-value < .05, so we should only keep those.
thresh = 1.97
stable_saliences = saliences.copy()
stable_saliences[np.abs(stability_saliences) <= thresh] = 0
stable_patterns = patterns.copy()
stable_patterns[np.abs(stability_patterns) <= thresh] = 0
