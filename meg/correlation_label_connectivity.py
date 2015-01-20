''' Checks whether there is a group difference in the connectivity map for a given seed '''

import mne
import numpy as np
from scipy import stats

bands = [[1, 4]]#, [4, 8], [8, 13], [13, 30], [30, 50]]
sx_fname = '/Users/sudregp/data/meg/inatt.txt'
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_5segs13p654.txt'
data_dir = '/Users/sudregp/data/meg/connectivity/'
lmethod = 'pca_flip'
cmethod = 5

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

# labels, label_colors = mne.labels_from_parc(subjs[0], parc='aparc')
nlabels=68#len(labels)
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
            data = data[il]
            subj_data[b].append(data.T)
    else:
        sx_data.append(0)
        fname = data_dir + '%s-%s-pli-imcoh-plv-wpli-pli2_unbiased-wpli2_debiased.npy'%(s,lmethod)
        conn = np.load(fname)[()]
        for b in range(len(bands)):
            data = conn[cmethod][:,:,b]
            data = data[il]
            subj_data[b].append(data.T)

cnt=0
for b in range(len(bands)):
    x = np.array(subj_data[b])
    val = []
    for i in range(x.shape[1]):
        slope, intercept, r_value, p_value, std_err = stats.linregress(x[:,i],sx_data)
        val.append(p_value)
    print bands[b]
    print 'Sources < .05 uncorrected:', sum(np.array(val)<.05)
    cnt+=sum(np.array(val)<.05)

n1 = len(sx_data)
print 'size1 =', n1
print cnt