''' Checks whether there is a group difference in the connectivity map for a given seed '''

import mne
import numpy as np
from scipy import stats

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
sx_fname = '/Users/sudregp/data/meg/inatt.txt'
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_5segs13p654.txt'
data_dir = '/Users/sudregp/data/meg/connectivity/'
lmethod = 'pca_flip'
cmethod = 0

selected_labels = []
# selected_labels = ['isthmuscingulate-rh', 'superiorfrontal-rh', 'inferiorparietal-rh', 'isthmuscingulate-lh', 'superiorfrontal-lh', 'inferiorparietal-lh']
# selected_labels = ['isthmuscingulate-rh', 'superiorfrontal-rh', 'inferiorparietal-rh']

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
res = np.recfromtxt(sx_fname, delimiter='\t')
sx = {}
for rec in res:
    sx[rec[0]] = rec[1]

print 'sx =',sx_fname
m = ['pli','imcoh','plv','wpli','pli2_unbiased','wpli2_debiased']
print lmethod, '-', m[cmethod]

labels, label_colors = mne.labels_from_parc(subjs[0], parc='aparc')
nlabels=len(labels)
il = np.tril_indices(nlabels, k=-1)
if len(selected_labels)>0:
    label_names = [l.name for l in labels]
    idx = [l for s in selected_labels for l, label in enumerate(label_names) if label == s]
    keep = [False]*len(il[0])
    for i in idx:
        for j in idx:
            keep = keep | ((il[0]==i) & (il[1]==j))
    il = [il[0][keep], il[1][keep]]


subj_data = [[] for b in range(len(bands))]
sx_data = []
for s in subjs:
    if sx.has_key(s):
        sx_data.append(sx[s])
        fname = data_dir + '%s-%s-pli-imcoh-plv-wpli-pli2_unbiased-wpli2_debiased.npy'%(s,lmethod)
        conn = np.load(fname)[()]
        for b in range(len(bands)):
            data = conn[cmethod][:,:,b]
            connectedness = []
            for i in range(nlabels):
                label_data = np.vstack([data[i,:], data[:,i].T])
                label_data[label_data==0] = np.nan
                connectedness.append(np.nanmean(label_data))
            subj_data[b].append(connectedness)

    # else:
    #     sx_data.append(0)
    #     fname = data_dir + '%s-%s-pli-imcoh-plv-wpli-pli2_unbiased-wpli2_debiased.npy'%(s,lmethod)
    #     conn = np.load(fname)[()]
    #     for b in range(len(bands)):
    #         data = conn[cmethod][:,:,b]
    #         connectedness = []
    #         for i in range(nlabels):
    #             label_data = np.vstack([data[i,:], data[:,i].T])
    #             label_data[label_data==0] = np.nan
    #             connectedness.append(np.nanmean(label_data))
    #             subj_data[b].append(connectedness)


for b, band in enumerate(bands):
    print band

    # Make arrays X and y such that :
    # X is 2d with X.shape[0] is the total number of observations to classify
    # y is filled with integers coding for the class to predict
    # We must have X.shape[0] equal to y.shape[0]
    X = np.array(subj_data[b])
    y = np.array(sx_data)

    from sklearn import preprocessing
    X = preprocessing.scale(X)

    s=[]
    from sklearn.linear_model import Lasso, LassoCV
    from sklearn.cross_validation import LeaveOneOut 
    cv = LeaveOneOut(X.shape[0])
    for train,test in cv:
        model = LassoCV(cv=20).fit(X[train], y[train])
        # print model.alpha_
        clf = Lasso(alpha=model.alpha_)
        clf.fit(X[train],y[train])
        s.append(np.abs(y[test]-clf.predict(X[test])))
    print '%.2f+-%.2f'%(np.mean(s),np.std(s))