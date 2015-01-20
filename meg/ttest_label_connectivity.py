''' Checks whether there is a group difference in the connectivity map for a given seed '''

import mne
import numpy as np
from scipy import stats

bands = [[1, 4]]#, [4, 8], [8, 13], [13, 30], [30, 50]]
g1_fname = '/Users/sudregp/data/meg/nv_subjs.txt'
g2_fname = '/Users/sudregp/data/meg/persistent_subjs_unmed.txt'
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_5segs13p654.txt'
data_dir = '/Users/sudregp/data/meg/connectivity/'
lmethod = 'pca_flip'
cmethod = 5
fdr = 0  # 0 for none

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
g1_subjs=[]
g2_subjs=[]
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

cnt=0
for b in range(len(bands)):
    x = np.array(g1_data[b])
    y = np.array(g2_data[b])
    val = [stats.ttest_ind(x[:,i],y[:,i],equal_var=False)[1] for i in range(x.shape[1])]
    print bands[b]
    print 'Sources < .05 uncorrected:', sum(np.array(val)<.05)
    cnt+=sum(np.array(val)<.05)
    best_connections = ['%s : %s (%.2g)'%(labels[il[0][idx]].name, labels[il[1][idx]].name, val[idx]) for idx in np.argsort(val) if val[idx]<.05]
    # print best_connections[:5]
    if fdr > 0:
        reject_fdr, pval_fdr = mne.stats.fdr_correction(val, alpha=fdr, method='indep')
        print 'Sources < %.2f (FDR-corrected):'%fdr, sum(np.array(pval_fdr)<fdr)


n1 = len(g1_data[0])
n2 = len(g2_data[0])
print 'size1 =', n1
print 'size2 =', n2
print cnt