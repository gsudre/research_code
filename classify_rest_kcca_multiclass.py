# plots the 2-dimensional representaiton learned with LDA look
# MEG and fMRI data

import os
import numpy as np
import matplotlib.pyplot as plt
home = os.path.expanduser('~')
import sys
sys.path.append(home + '/research_code/PyKCCA-master/')
from sklearn import preprocessing

seeds = ['net7_rACC']
# seeds = ['net1_lMidOccipital','net1_lParaHippo','net1_rMidOccipital',
#          'net1_rParaHippo','net2_lParaCentral','net2_lPostCentral']
# seeds = ['net2_lPreCentral','net2_rParaCentral','net2_rPostCentral',
#          'net2_rPreCentral','net3_lFusiform','net3_lSuperiorParietal']
# seeds = ['net2_rParaCentral','net2_rPostCentral',
#          'net2_rPreCentral','net3_lFusiform','net3_lSuperiorParietal']
# seeds = ['net3_rFusiform','net3_rSuperiorParietal','net4_lCingulate',
#          'net4_lInsula','net4_rCingulate','net4_rInsula','net6_lSupra']
# seeds = ['net6_rSupra','net7_lACC','net7_lITG','net7_rACC','net7_rITG']
bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55]]#, [65, 100]]

for s, seed in enumerate(seeds):
    phen = np.recfromcsv(home + '/data/overlap_resting/subjs.csv')

    print 'Loading fMRI data for %s...'%seed 
    data_dir = home + '/data/results/fmri_Yeo/seeds/' + seed + '/' 
    data = np.genfromtxt(data_dir + 'joel_all_corr_downsampled.txt')
    data = data[:,6:]  # removes x,y,z and i,j,k
    X_fmri, colors = [], []
    # load the order of subjects within the data matrix
    subjs_fname = home + '/data/fmri/joel_all.txt'
    fid = open(subjs_fname, 'r')
    subjs = [line.rstrip() for line in fid]
    fid.close()
    for rec in phen:
        subj_idx = subjs.index('%04d'%rec[0])
        if rec['dx']=='NV':
            X_fmri.append(data[:,subj_idx])
            colors.append('g')
        elif rec['dx']=='persistent':
            X_fmri.append(data[:,subj_idx])
            colors.append('r')
        else:
            X_fmri.append(data[:,subj_idx])
            colors.append('b')
    X_fmri = np.array(X_fmri)

    print 'Loading MEG data for %s...'%seed 
    data_dir = home + '/data/results/meg_Yeo/seeds/' + seed + '/'
    for b in bands:
        data = np.load(data_dir+'/correlations_%s-%s.npy'%(b[0],b[1]))[()]
        X_meg = [data[rec[1]] for rec in phen if rec['dx'] in ['NV','persistent','remission']]
        X_meg = np.array(X_meg).squeeze()
        # cleaning up MEG data. First, remove any subjects that have all NaNs
        idx = np.isnan(X_meg).all(axis=1)
        if np.sum(idx)>0:
            print 'Removing %d subjects'%np.sum(idx)
            X_meg = X_meg[~idx,:]
            if b==bands[0]:
                X_fmri = X_fmri[~idx,:]
                bad_subjs = np.nonzero(idx)[0].tolist()
                bad_subjs.sort()
                for i in bad_subjs[::-1]:
                    colors.pop(i)
        # remove features that have NaNs, but keep track of them for the future
        idx = np.isnan(X_meg).any(axis=0) # mask of features with at least 1 NaN
        X_meg = X_meg[:,~idx]
        print 'Features left: %d/%d'%(X_meg.shape[1],len(idx))

        X_meg = preprocessing.scale(X_meg)
        X_fmri = preprocessing.scale(X_fmri)

        X = np.hstack([X_fmri, X_meg])

        import kcca, kernels
        ncomps = 40
        kernel = kernels.LinearKernel()
        cca = kcca.KCCA(kernel, kernel, regularization=1e-5, decomp='full',
                        method='kettering_method', scaler1=lambda x:x, 
                        scaler2=lambda x:x)
        # it's fine to learn the map outside cross-validation since 
        # we don't care about the labels
        cca = cca.fit(X_fmri,X_meg)
        X_fmri2,X_meg2 = cca.transform(X_fmri,X_meg)
        X = np.hstack([X_fmri2[:,:ncomps], X_meg2[:,:ncomps]])

        # use LDA
        from sklearn import lda, preprocessing, svm
        from sklearn.metrics import accuracy_score
        from sklearn.dummy import DummyClassifier
        le = preprocessing.LabelEncoder()
        le.fit(colors)
        y = le.transform(colors)
        clf = lda.LDA(n_components=2)

        test_scores, train_scores, dummy_scores = [],[],[]
        from sklearn.cross_validation import LeaveOneOut, StratifiedShuffleSplit
        nfolds=40
        cv = LeaveOneOut(len(y))#StratifiedShuffleSplit(y,n_iter=nfolds,test_size=.1)
        svc = svm.SVC()
        for oidx, (train, test) in enumerate(cv):
            # print '=========\ncv %d/%d\n========='%(oidx+1,nfolds)
            X_train, X_test = X[train], X[test]
            y_train, y_test = y[train], y[test]
            clf.fit(X_train,y_train)
            X_train = clf.transform(X_train)
            X_test = clf.transform(X_test)

            svc.fit(X_train, y_train)
            train_scores.append(accuracy_score(svc.predict(X_train),y_train))
            test_scores.append(accuracy_score(svc.predict(X_test),y_test))
            dumb = DummyClassifier(strategy='most_frequent')
            dumb.fit(X_train, y_train)
            dummy_scores.append(accuracy_score(dumb.predict(X_test),y_test))
        print seed, b
        print 'dummy: %.3f'%np.mean(dummy_scores)
        print 'test: %.3f'%np.mean(test_scores)
        print 'train: %.3f'%np.mean(train_scores)
        

