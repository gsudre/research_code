# plots the fMRI data in 2D to look for outliers

import os
import numpy as np
import matplotlib.pyplot as plt
from math import sqrt, ceil
home = os.path.expanduser('~')

seeds = ['net1_lMidOccipital','net1_lParaHippo','net6_lSupra']
seeds = ['net1_lMidOccipital','net1_lParaHippo','net1_rMidOccipital',
         'net1_rParaHippo','net2_lParaCentral','net2_lPostCentral',
         'net2_lPreCentral','net2_rParaCentral','net2_rPostCentral',
         'net2_rPreCentral','net3_lFusiform','net3_lSuperiorParietal',
         'net3_rFusiform','net3_rSuperiorParietal','net4_lCingulate',
         'net4_lInsula','net4_rCingulate','net4_rInsula','net6_lSupra',
         'net6_rSupra','net7_lACC','net7_lITG','net7_rACC','net7_rITG']
seeds = ['net1_lMidOccipital','net1_lParaHippo',
         'net1_rParaHippo','net2_lParaCentral','net2_lPostCentral',
         'net2_lPreCentral','net2_rParaCentral','net2_rPostCentral',
         'net2_rPreCentral','net3_lFusiform','net3_lSuperiorParietal',
         'net3_rFusiform','net3_rSuperiorParietal','net4_lCingulate',
         'net4_lInsula','net4_rCingulate','net4_rInsula','net6_lSupra',
         'net6_rSupra','net7_lACC','net7_lITG','net7_rACC','net7_rITG']
# seeds = ['net1_lMidOccipital']

# load the order of subjects within the data matrix
subjs_fname = home + '/data/fmri/joel_all.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

fig1 = plt.figure(1)
fig2 = plt.figure(2)
nplots = ceil(sqrt(len(seeds)))
for s, seed in enumerate(seeds):
    print 'Loading fMRI data for %s...'%seed 
    data_dir = home + '/data/results/fmri_Yeo/seeds/' + seed + '/' 
    data = np.genfromtxt(data_dir + 'joel_all_corr_downsampled.txt')
    data = data[:,6:]  # removes x,y,z and i,j,k
    X, colors = [], []

    #####
    # get data from overlap with MEG
    #####
    phen = np.recfromcsv(home + '/data/overlap_resting/subjs.csv')
    for rec in phen:
        subj_idx = subjs.index('%04d'%rec[0])
        X.append(data[:,subj_idx])
        if rec['dx']=='NV':
            colors.append('g')
        elif rec['dx']=='persistent':
            colors.append('r')
        else:
            colors.append('b')

    # #####
    # # or use all fMRI data
    # #####
    # g1_fname = home + '/data/fmri/joel_nvs.txt'
    # g2_fname = home + '/data/fmri/joel_persistent.txt'
    # g3_fname = home + '/data/fmri/joel_remission.txt'
    # fid1 = open(g1_fname, 'r')
    # fid2 = open(g2_fname, 'r')
    # fid3 = open(g3_fname, 'r')
    # g1 = [line.rstrip() for line in fid1]
    # g2 = [line.rstrip() for line in fid2]
    # g3 = [line.rstrip() for line in fid3]
    # for sidx, subj in enumerate(subjs):
    #     X.append(data[:,sidx])
    #     if subj in g1:
    #         colors.append('g')
    #     elif subj in g2:
    #         colors.append('r')
    #     else:
    #         colors.append('b')

    X = np.array(X)

    # compute the 2 dimensional representation
    from sklearn import manifold
    mds = manifold.MDS(2, max_iter=100, n_init=1)
    Y = mds.fit_transform(X)

    # plotting
    plt.figure(1)
    plt.subplot(nplots,nplots,s+1)
    plt.scatter(Y[:, 0], Y[:, 1], color=colors)
    plt.title(seed)

    # just for fun, let's try to use LDA
    from sklearn import lda, preprocessing
    le = preprocessing.LabelEncoder()
    le.fit(colors)
    y = le.transform(colors)
    Y = lda.LDA(n_components=2).fit_transform(X, y)
    plt.figure(2)
    plt.subplot(nplots,nplots,s+1)
    plt.scatter(Y[:, 0], Y[:, 1], color=colors)
    plt.title(seed)
