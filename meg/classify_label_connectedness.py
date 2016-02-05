''' Checks whether there is a group difference in the connectedness map for a given seed '''

import mne
import numpy as np
from scipy import stats

bands = [[1, 4]]#, [4, 8], [8, 13], [13, 30], [30, 50]]
g1_fname = '/Users/sudregp/data/meg/remitted_subjs.txt'
g2_fname = '/Users/sudregp/data/meg/persistent_subjs.txt'
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_5segs13p654.txt'
data_dir = '/Users/sudregp/data/meg/connectivity/'
lmethod = 'pca_flip'
cmethod = 5

selected_labels = []
# selected_labels = ['isthmuscingulate-rh', 'superiorfrontal-rh', 'inferiorparietal-rh', 'isthmuscingulate-lh', 'superiorfrontal-lh', 'inferiorparietal-lh']
# selected_labels = ['isthmuscingulate-rh', 'superiorfrontal-rh', 'inferiorparietal-rh']

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]

print 'g1 =',g1_fname
print 'g2 =',g2_fname
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


g1_data = [[] for b in range(len(bands))]
g2_data = [[] for b in range(len(bands))]
for s in subjs:
    fname = data_dir + '%s-%s-pli-imcoh-plv-wpli-pli2_unbiased-wpli2_debiased.npy'%(s,lmethod)
    conn = np.load(fname)[()]
    for b in range(len(bands)):
        data = conn[cmethod][:,:,b]
        connectedness = []
        for i in range(nlabels):
            label_data = np.vstack([data[i,:], data[:,i].T])
            label_data[label_data==0] = np.nan
            connectedness.append(np.nanmean(label_data))
        if s in g1:
            g1_data[b].append(connectedness)
        elif s in g2:
            g2_data[b].append(connectedness)

cnt=0
for b in range(len(bands)):
    x = np.array(g1_data[b])
    y = np.array(g2_data[b])
    val = [stats.ttest_ind(x[:,i],y[:,i])[1] for i in range(x.shape[1])]
    print bands[b]
    print 'Sources < .05 uncorrected:', sum(np.array(val)<.05)
    cnt+=sum(np.array(val)<.05)

n1 = len(g1_data[0])
n2 = len(g2_data[0])
print 'size1 =', n1
print 'size2 =', n2
print cnt

if n1>n2:
    weight = {0 : n1/float(n2)}
else:
    weight = {1 : n2/float(n1)}

for b, band in enumerate(bands):
    print band

    # Make arrays X and y such that :
    # X is 2d with X.shape[0] is the total number of observations to classify
    # y is filled with integers coding for the class to predict
    # We must have X.shape[0] equal to y.shape[0]
    X = np.vstack([np.matrix(g1_data[b]), np.matrix(g2_data[b])])
    y = np.hstack([np.zeros([len(g1_data[b])]),np.ones([len(g2_data[b])])])

    from sklearn import cross_validation
    from sklearn.linear_model import LogisticRegression
    from sklearn.cross_validation import LeaveOneOut 

    from sklearn import preprocessing
    X = preprocessing.scale(X)



