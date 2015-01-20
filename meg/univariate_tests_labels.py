''' Checks whether there is a group difference in the connectivity '''

import mne
import numpy as np
from scipy import stats

bands = [[1, 4]]#, [4, 8]]#, [8, 13], [13, 30]]#, [30, 50]]
g1_fname = '/Users/sudregp/data/meg/nv_subjs.txt'
g2_fname = '/Users/sudregp/data/meg/persistent_subjs.txt'
g3_fname = '/Users/sudregp/data/meg/remitted_subjs.txt'
inatt_fname = '/Users/sudregp/data/meg/inatt.txt'
hi_fname = '/Users/sudregp/data/meg/hi.txt'
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_5segs13p654.txt'
data_dir = '/Users/sudregp/data/meg/connectivity/'
lmethod = 'pca_flip'
cmethod = 5
alpha=.05
fdr = .05  # 0 for none
mean = False
ipsiOnly = True

selected_labels = []
# selected_labels = ['isthmuscingulate', 'inferiorparietal', 'superiorfrontal']  # DMN 
# selected_labels = ['superiorparietal', 'precentral'] # dorsal attn
# selected_labels = ['superiorparietal', 'precentral'] # dorsal attn Philip
# selected_labels = ['supramarginal', 'insula'] # ventral attn
selected_labels = ['isthmuscingulate', 'lateralorbitofrontal'] #affective
# selected_labels = ['rostralmiddlefrontal', 'superiorfrontal', 'caudalmiddlefrontal', 'insula', 'superiorparietal'] #cognitivecontrol
# selected_labels = ['precentral', 'postcentral'] #sensorimotor
# selected_labels = ['superiorfrontal', 'isthmuscingulate', 'parstriangularis', 'bankssts', 'insula'] #social

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid3 = open(g3_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
g3 = [line.rstrip() for line in fid3]
res = np.recfromtxt(inatt_fname, delimiter='\t')
inatt = {}
for rec in res:
    inatt[rec[0]] = rec[1]
res = np.recfromtxt(hi_fname, delimiter='\t')
hi = {}
for rec in res:
    hi[rec[0]] = rec[1]

print 'g1 =',g1_fname
print 'g2 =',g2_fname
print 'g3 =',g3_fname
m = ['pli','imcoh','plv','wpli','pli2_unbiased','wpli2_debiased']
print lmethod, '-', m[cmethod]

fid = open('/Users/sudregp/tmp/u.csv','w')

labels, label_colors = mne.labels_from_parc(subjs[0], parc='aparc')
nlabels=len(labels)
il = np.tril_indices(nlabels, k=-1)
label_names = [l.name for l in labels]
if not ipsiOnly:
    selected_labels = ['%s-%s'%(l,h) for l in selected_labels for h in ['lh','rh']]
    if len(selected_labels)>0:
        idx = [l for s in selected_labels for l, label in enumerate(label_names) if label == s]
        # make sure we found all labels
        if len(idx)!=len(selected_labels):
            raise ValueError('Did not find all selected labels!')
        keep = [False]*len(il[0])
        for i in idx:
            for j in idx:
                keep = keep | ((il[0]==i) & (il[1]==j))
        il = [il[0][keep], il[1][keep]]
else:
    hemi_il = []
    for hemi in ['lh','rh']:
        if len(selected_labels)>0:
            hemi_selected_labels = ['%s-%s'%(l,hemi) for l in selected_labels]
        else:
            hemi_selected_labels = [l for l in label_names if l.find(hemi)>0]
        idx = [l for s in hemi_selected_labels for l, label in enumerate(label_names) if label == s]
        # make sure we found all labels
        if len(idx)!=len(hemi_selected_labels):
            raise ValueError('Did not find all selected labels!')
        keep = [False]*len(il[0])
        for i in idx:
            for j in idx:
                keep = keep | ((il[0]==i) & (il[1]==j))
        hemi_il.append([il[0][keep], il[1][keep]])
    il = []
    il.append(np.hstack([hemi_il[0][0],hemi_il[1][0]]))
    il.append(np.hstack([hemi_il[0][1],hemi_il[1][1]]))

g1_data = [[] for b in range(len(bands))]
g2_data = [[] for b in range(len(bands))]
g3_data = [[] for b in range(len(bands))]
g1_subjs=[]
g2_subjs=[]
g3_subjs=[]
g2_inatt = []
g2_hi = []
g3_inatt = []
g3_hi = []
for s in subjs:
    fname = data_dir + '%s-%s-pli-imcoh-plv-wpli-pli2_unbiased-wpli2_debiased.npy'%(s,lmethod)
    conn = np.load(fname)[()]
    for b in range(len(bands)):
        data = conn[cmethod][:,:,b]
        data = data[il]
        if s in g1:
            g1_data[b].append(data.T)
            if b==0:
                g1_subjs.append(s)
        elif s in g2:
            g2_data[b].append(data.T)
            if b==0:
                g2_subjs.append(s)
                g2_inatt.append(inatt[s])
                g2_hi.append(hi[s])
        elif s in g3:
            g3_data[b].append(data.T)
            if b==0:
                g3_subjs.append(s)
                g3_inatt.append(inatt[s])
                g3_hi.append(hi[s])

inatt = g2_inatt + g3_inatt
hi = g2_hi + g3_hi
for b in range(len(bands)):
    # print bands[b]
    x = np.array(g1_data[b])
    y = np.array(g2_data[b])
    z = np.array(g3_data[b])
    res = []
    if not mean:
        nfeats = x.shape[1]
        print nfeats, 'connections'
        val = [[] for i in range(10)]
        for i in range(nfeats):
            f, pval = stats.f_oneway(x[:,i],y[:,i],z[:,i]) 
            val[0].append(pval)
            f, pval = stats.kruskal(x[:,i],y[:,i],z[:,i]) 
            val[1].append(pval)
            f, pval = stats.ttest_ind(x[:,i],y[:,i]) 
            val[2].append(pval)
            f, pval = stats.ttest_ind(x[:,i],z[:,i]) 
            val[3].append(pval)
            f, pval = stats.ttest_ind(y[:,i],z[:,i]) 
            val[4].append(pval)
            f, pval = stats.mannwhitneyu(x[:,i],y[:,i]) 
            val[5].append(2*pval)
            f, pval = stats.mannwhitneyu(x[:,i],z[:,i]) 
            val[6].append(2*pval)
            f, pval = stats.mannwhitneyu(y[:,i],z[:,i]) 
            val[7].append(2*pval)
            adhd = np.hstack([y[:, i], z[:,i]])
            slope, intercept, r_value, pval, std_err = stats.linregress(adhd,inatt)
            val[8].append(pval)
            slope, intercept, r_value, pval, std_err = stats.linregress(adhd,hi)
            val[9].append(pval)
        for pvals in val:
            reject_fdr, pval_fdr = mne.stats.fdr_correction(pvals, alpha=fdr, method='indep')
            res.append('%d | %d | %d'%(sum(np.array(pvals)<alpha),sum(np.array(pval_fdr)<fdr), sum(np.array(pvals)<(alpha/nfeats))))
        fid.write(','.join(str(i) for i in res) + ',,')
    else:
        f, pval = stats.f_oneway(np.mean(x,axis=1),np.mean(y,axis=1),np.mean(z,axis=1))
        res.append(pval) 
        f, pval = stats.kruskal(np.mean(x,axis=1),np.mean(y,axis=1),np.mean(z,axis=1))
        res.append(pval) 
        f, pval = stats.ttest_ind(np.mean(x,axis=1),np.mean(y,axis=1),equal_var=False) 
        res.append(pval)
        f, pval = stats.ttest_ind(np.mean(x,axis=1),np.mean(z,axis=1),equal_var=False) 
        res.append(pval)
        f, pval = stats.ttest_ind(np.mean(y,axis=1),np.mean(z,axis=1),equal_var=False) 
        res.append(pval)
        f, pval = stats.mannwhitneyu(np.mean(x,axis=1),np.mean(y,axis=1)) 
        res.append(2*pval)
        f, pval = stats.mannwhitneyu(np.mean(x,axis=1),np.mean(z,axis=1)) 
        res.append(2*pval)
        f, pval = stats.mannwhitneyu(np.mean(y,axis=1),np.mean(z,axis=1)) 
        res.append(2*pval)
        adhd = np.hstack([np.mean(y,axis=1),np.mean(z,axis=1)])
        slope, intercept, r_value, pval, std_err = stats.linregress(adhd,inatt)
        res.append(pval)
        slope, intercept, r_value, pval, std_err = stats.linregress(adhd,hi)
        res.append(pval)
        print ','.join(str(i) for i in res)
        fid.write(','.join(str(i) for i in res) + ',,')
fid.close()

n1 = len(g1_data[0])
n2 = len(g2_data[0])
n3 = len(g3_data[0])
print 'size1 =', n1
print 'size2 =', n2
print 'size3 =', n3

