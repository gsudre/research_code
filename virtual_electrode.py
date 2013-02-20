import mne
import numpy as np


def calculate_weights(forward, cov, reg=0):

    inv_Cb = np.linalg.pinv(cov.data[:306, :306] + reg * np.eye(306))
    L = forward['sol']['data']
    nvectors = L.shape[1]
    # If we have more than one orientation per source, find the optimum
    # orientation following Sekihara et al. Asymptotic SNR of scalar and vector
    # minimum-variance beamformers for neuromagnetic source reconstruction. IEEE
    # Trans. Biomed. Eng, No 10, Vol. 51, 2004, pp 1726-1734. The code is also
    # somewhat borrowed from the Fieldtrip implementation.
    if forward['nsource'] < nvectors:
        optimal_orientation = np.zeros([3, forward['nsource']])
        for dip in range(forward['nsource']):
            # Separate the lead field for 3 orthogonal components
            ori = L[:306, (3 * dip):(3 * dip + 3)]
            U, S, V = np.linalg.svd(np.linalg.pinv(np.dot(ori.T, np.dot(inv_Cb, ori))))

            # The optimum orientation is the eigenvector that corresponds to the
            # MAXIMUM eigenvalue. However, we need to double check that this is
            # the case, because for single sphere head model, one of the
            # eigenvectors corresponds to the radial direction, giving lead fields
            # that are zero (to within machine precission). The eigenvalue
            # corresponding to this eigenvector can actually be the smallest and
            # can give the optimum (but wrong) Z-value!)

            ori1 = U[:, 1] / np.linalg.norm(U[:, 1])
            ori2 = U[:, 2] / np.linalg.norm(U[:, 2])

            # We only need to compare the eigenvectors that correspond to the two
            # biggest eigen values!

            L1 = np.dot(ori, ori1)
            L2 = np.dot(ori, ori2)

            if np.linalg.norm(L1) / np.linalg.norm(L2) < 1e-6:
            # the first orientation seems to be the silent orientation use the
            # second orientation instead
                optimal_orientation[:, dip] = ori2
            else:
                optimal_orientation[:, dip] = ori1
    else:
        optimal_orientation = forward['source_rr']

    weight = np.zeros([forward['nsource'], 306])
    for dip in range(forward['nsource']):
        gain = L[:306, dip]
        num = np.dot(gain.T, inv_Cb)
        den = np.dot(num, gain)  # this is a scalar
        weight[dip, :] = num / den

    return weight
