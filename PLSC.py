import mne
import pylab as pl
import numpy as np
import virtual_electrode as ve
import env
import find_good_segments as fgs
import glob
import spreadsheet
import os
from scipy import stats
from openpyxl.reader.excel import load_workbook
import datetime
import pdb


def PLSC(X, Y, groups, num_comps=2):
    ''' Returns results of Partial Least Squares Correlation. groups is a list of 2-index lists, such as [[0, 10]] '''

    # first, center and normalize matrices within groups. We remove the mean of each column, and then normalize it so that the sum squared of a column equals to 1.
    Xn = np.empty_like(X)
    Yn = np.empty_like(Y)
    for g in groups:
        Xg = X[g[0]:g[1], :]
        Yg = Y[g[0]:g[1], :]

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
        SSy[SSy == 0] = 1e-16
        signs = np.sign(Yc)
        signs[signs == 0] = 1
        Yn[g[0]:g[1], :] = signs * np.sqrt(Yc ** 2 / SSy)

    # now, compute the correlation matrix within groups
    R = np.zeros([num_seeds * num_groups, Xn.shape[1]])
    cnt = 0
    for g in groups:
        Xg = Xn[g[0]:g[1], :]
        Yg = Yn[g[0]:g[1], :]

        R[cnt:(cnt + num_seeds), :] = np.dot(Yg.T, Xg)
        cnt += num_seeds

    # now we run SVD on the correlation matrix
    U, S, Vh = np.linalg.svd(R)
    V = Vh.T

    return S[:num_comps], V[:, :num_comps]


X = [[2, 5, 6, 1, 9, 1, 7, 6, 2, 1, 7, 3],
    [4, 1, 5, 8, 8, 7, 2, 8, 6, 4, 8, 2],
    [5, 8, 7, 3, 7, 1, 7, 4, 5, 1, 4, 3],
    [3, 3, 7, 6, 1, 1, 10, 2, 2, 1, 7, 4],
    [2, 3, 8, 7, 1, 6, 9, 1, 8, 8, 1, 6],
    [1, 7, 3, 1, 1, 3, 1, 8, 1, 3, 9, 5],
    [9, 0, 7, 1, 8, 7, 4, 2, 3, 6, 2, 7],
    [8, 0, 6, 5, 9, 7, 4, 4, 2, 10, 3, 8],
    [7, 7, 4, 5, 7, 6, 7, 6, 5, 4, 8, 8]]

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

num_groups = len(groups)
num_seeds = Y.shape[1]

cortex = X
subcortex = Y
groups = [[0, 3], [3, 6], [6, 9]]
sv, saliences = PLSC(X, Y, groups)
