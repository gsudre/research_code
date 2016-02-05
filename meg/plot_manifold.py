# plots the fMRI data in 2D to look for outliers

import os
import numpy as np
import matplotlib.pyplot as plt
home = os.path.expanduser('~')

# seeds = ['net1_lMidOccipital']
seeds = ['net1_lMidOccipital','net1_lParaHippo','net1_rMidOccipital',
         'net1_rParaHippo','net2_lParaCentral','net2_lPostCentral']
seeds = ['net2_lPreCentral','net2_rParaCentral','net2_rPostCentral',
         'net2_rPreCentral','net3_lFusiform','net3_lSuperiorParietal']
seeds = ['net2_rParaCentral','net2_rPostCentral',
         'net2_rPreCentral','net3_lFusiform','net3_lSuperiorParietal']
seeds = ['net3_rFusiform','net3_rSuperiorParietal','net4_lCingulate',
         'net4_lInsula','net4_rCingulate','net4_rInsula','net6_lSupra']
seeds = ['net6_rSupra','net7_lACC','net7_lITG','net7_rACC','net7_rITG']
bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]

fig1 = plt.figure(1)
fig2 = plt.figure(2)
nrows = len(seeds)
ncols = len(bands)
cnt = 1
for s, seed in enumerate(seeds):
    print 'Loading MEG data for %s...'%seed 
    data_dir = home + '/data/results/meg_Yeo/seeds/' + seed + '/'

    for b in bands:
        X, colors = [], []
        data = np.load(data_dir+'/correlations_%s-%s.npy'%(b[0],b[1]))[()]
        # #####
        # # get data from overlap with fMRI
        # #####
        # phen = np.recfromcsv(home + '/data/overlap_resting/subjs.csv')
        # for rec in phen:
        #     X.append(data[rec[1]])
        #     if rec['dx'] == 'NV':
        #         colors.append('g')
        #     elif rec['dx'] == 'persistent':
        #         colors.append('r')
        #     else:
        #         colors.append('b') 

        #####
        # or use all MEG data
        #####
        subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
        g1_fname = '/Users/sudregp/data/meg/nv_subjs.txt'
        g2_fname = '/Users/sudregp/data/meg/persistent_subjs.txt'
        g3_fname = '/Users/sudregp/data/meg/remitted_subjs.txt'
        fid1 = open(g1_fname, 'r')
        fid2 = open(g2_fname, 'r')
        fid3 = open(g3_fname, 'r')
        g1 = [line.rstrip() for line in fid1]
        g2 = [line.rstrip() for line in fid2]
        g3 = [line.rstrip() for line in fid3]
        fid = open(subjs_fname, 'r')
        subjs = [line.rstrip() for line in fid]
        for sidx, subj in enumerate(subjs):
            X.append(data[subj])
            if subj in g1:
                colors.append('g')
            elif subj in g2:
                colors.append('r')
            else:
                colors.append('b')

        X = np.array(X).squeeze()

        # cleaning up MEG data. First, remove any subjects that have all NaNs
        idx = np.isnan(X).all(axis=1)
        if np.sum(idx)>0:
            print 'Removing %d subjects'%np.sum(idx)
            X = X[~idx,:]
            bad_subjs = np.nonzero(idx)[0].tolist()
            bad_subjs.sort()
            for i in bad_subjs[::-1]:
                colors.pop(i)
        # remove features that have NaNs, but keep track of them for the future
        idx = np.isnan(X).any(axis=0) # mask of features with at least 1 NaN
        X = X[:,~idx]
        print 'Features left: %d/%d'%(X.shape[1],len(idx))

        # compute the 2 dimensional representation
        from sklearn import manifold
        mds = manifold.MDS(2, max_iter=100, n_init=1)
        Y = mds.fit_transform(X)

        # plotting
        plt.figure(1)
        plt.subplot(nrows,ncols,cnt)
        plt.scatter(Y[:, 0], Y[:, 1], color=colors)
        plt.xticks([])
        plt.yticks([])
        plt.title('%s: %d-%d'%(seed,b[0],b[1]))

        # just for fun, let's try to use LDA
        from sklearn import lda, preprocessing
        le = preprocessing.LabelEncoder()
        le.fit(colors)
        y = le.transform(colors)
        Y = lda.LDA(n_components=2).fit_transform(X, y)
        plt.figure(2)
        plt.subplot(nrows,ncols,cnt)
        plt.scatter(Y[:, 0], Y[:, 1], color=colors)
        plt.xticks([])
        plt.yticks([])
        plt.title('%s: %d-%d'%(seed,b[0],b[1]))

        cnt+=1
