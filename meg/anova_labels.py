''' Checks whether there is a group difference in the connectivity '''

import mne
import numpy as np
from scipy import stats

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
g1_fname = '/Users/sudregp/data/meg/nv_subjs.txt'
g2_fname = '/Users/sudregp/data/meg/persistent_subjs.txt'
g3_fname = '/Users/sudregp/data/meg/remitted_subjs.txt'
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_5segs13p654.txt'
data_dir = '/Users/sudregp/data/meg/connectivity/'
lmethod = 'pca_flip'
cmethod = 5
alpha=.05
fdr = .05  # 0 for none
mean = True

selected_labels = []
selected_labels = ['isthmuscingulate-rh', 'superiorfrontal-rh', 'inferiorparietal-rh', 'isthmuscingulate-lh', 'superiorfrontal-lh', 'inferiorparietal-lh']  # DMN
# selected_labels = ['isthmuscingulate-rh', 'superiorfrontal-rh', 'inferiorparietal-rh']
# selected_labels = ['isthmuscingulate-lh', 'superiorfrontal-lh', 'inferiorparietal-lh']

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid3 = open(g3_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
g3 = [line.rstrip() for line in fid3]

print 'g1 =',g1_fname
print 'g2 =',g2_fname
print 'g3 =',g3_fname
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
g3_data = [[] for b in range(len(bands))]
g1_subjs=[]
g2_subjs=[]
g3_subjs=[]
for s in subjs:
    fname = data_dir + '%s-%s-pli-imcoh-plv-wpli-pli2_unbiased-wpli2_debiased.npy'%(s,lmethod)
    conn = np.load(fname)[()]
    for b in range(len(bands)):
        data = conn[cmethod][:,:,b]
        data = data[il]
        if s in g1:
            g1_data[b].append(data.T)
            g1_subjs.append(s)
        elif s in g2:
            g2_data[b].append(data.T)
            g2_subjs.append(s)
        elif s in g3:
            g3_data[b].append(data.T)
            g3_subjs.append(s)

cnt=0
for b in range(len(bands)):
    print bands[b]
    x = np.array(g1_data[b])
    y = np.array(g2_data[b])
    z = np.array(g3_data[b])
    if not mean:
        nfeats = x.shape[1]
        val = []
        for i in range(nfeats):
            f, pval = stats.kruskal(x[:,i],y[:,i],z[:,i]) 
            val.append(pval) 
            #= [stats.ttest_ind(x[:,i],y[:,i],equal_var=False)[1] for i in range(x.shape[1])]
        print 'Sources < %.2f uncorrected:'%alpha, sum(np.array(val)<alpha)
        cnt+=sum(np.array(val)<alpha)
        # best_connections = ['%s : %s (%.2g)'%(labels[il[0][idx]].name, labels[il[1][idx]].name, val[idx]) for idx in np.argsort(val) if val[idx]<alpha]
        # print best_connections[:5]
        if fdr > 0:
            reject_fdr, pval_fdr = mne.stats.fdr_correction(val, alpha=fdr, method='indep')
            print 'Sources < %.2f (FDR-corrected):'%fdr, sum(np.array(pval_fdr)<fdr)
        bf = alpha/len(val)
        print 'Sources < %.2f (Bonferroni):'%bf, sum(np.array(val)<bf)
    else:
        res = []
        f, pval = stats.kruskal(np.mean(x,axis=1),np.mean(y,axis=1),np.mean(z,axis=1))
        res.append(pval) 
        f, pval = stats.ttest_ind(np.mean(x,axis=1),np.mean(y,axis=1),equal_var=False) 
        res.append(pval)
        f, pval = stats.ttest_ind(np.mean(x,axis=1),np.mean(z,axis=1),equal_var=False) 
        res.append(pval)
        f, pval = stats.ttest_ind(np.mean(y,axis=1),np.mean(x,axis=1),equal_var=False) 
        res.append(pval)
        print res


n1 = len(g1_data[0])
n2 = len(g2_data[0])
n3 = len(g3_data[0])
print 'size1 =', n1
print 'size2 =', n2
print 'size3 =', n3
print cnt