import numpy as np
import env
import scipy


def procrustes(Vorig, Vresamp, Sresamp):
    ''' Following the algorithm in McIntosha and Lobaugh, 2004 ''' 
    N, O, Ph = np.linalg.svd(np.dot(Vorig.T, Vresamp), full_matrices=False)
    P = Ph.T

    Q = np.dot(N, P.T)
    if Sresamp.ndim == 1:
        Sresamp = Sresamp * np.eye(len(Sresamp))

    Vhat = np.dot(Vresamp, np.dot(Sresamp, Q))
    Shat = np.sqrt(np.sum(Vhat ** 2, axis=0))

    return Vhat, Shat




# num_perms = sv_perm.shape[-1]
