''' Checks whether there is a group difference in the connectivity '''

import mne
import numpy as np
from scipy import stats

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
g1_fname = '/Users/sudregp/data/meg/nv_subjs.txt'
g2_fname = '/Users/sudregp/data/meg/persistent_subjs.txt'
g3_fname = '/Users/sudregp/data/meg/remitted_subjs.txt'
inatt_fname = '/Users/sudregp/data/meg/inatt.txt'
hi_fname = '/Users/sudregp/data/meg/hi.txt'
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_5segs13p654.txt'
data_dir = '/Users/sudregp/data/meg/connectivity/Yeo-Hillebrand/'
lmethod = 'pca_flip'
cmethod = 5
alpha=.05
fdr = .05  # 0 for none
mean = False
network = 'frontoparietal'


networks = ['visual','somatomotor','dorsal','ventral','limbic','frontoparietal','default']

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
print lmethod, '-', m[cmethod], '-', network

fid = open('/Users/sudregp/tmp/u.csv','w')

g1_data = [[] for b in range(len(bands))]
g2_data = [[] for b in range(len(bands))]
g3_data = [[] for b in range(len(bands))]
bad_features = [[] for b in range(len(bands))]
g1_subjs=[]
g2_subjs=[]
g3_subjs=[]
g2_inatt = []
g2_hi = []
g3_inatt = []
g3_hi = []
for s in subjs:
    fname = data_dir + '%s-7Networks_%d-lh-%s-pli-imcoh-plv-wpli-pli2_unbiased-wpli2_debiased.npy'%(s,networks.index(network)+1,lmethod)
    lconn_all = np.load(fname)[()]
    lil = np.tril_indices(lconn_all.shape[1], k=-1)
    fname = data_dir + '%s-7Networks_%d-rh-%s-pli-imcoh-plv-wpli-pli2_unbiased-wpli2_debiased.npy'%(s,networks.index(network)+1,lmethod)
    rconn_all = np.load(fname)[()]
    ril = np.tril_indices(rconn_all.shape[1], k=-1)
    for b in range(len(bands)):
        lconn = lconn_all[cmethod,:,:,b]
        rconn = rconn_all[cmethod,:,:,b]
        # find any rows or columns that are all zeros and mark them as NaN to further be removed
        lconn[:,~lconn.any(axis=0)]=np.nan
        lconn[~lconn.any(axis=1),:]=np.nan
        rconn[:,~rconn.any(axis=0)]=np.nan
        rconn[~rconn.any(axis=1),:]=np.nan
        data = np.hstack([lconn[lil], rconn[ril]])
        # mark any features with NaNs for future removal from all subjects, because this particular usbject didn't have any vertices in the label
        # bad_features[b].append(np.nonzero(np.isnan(data))[0])
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
    # first, we delete all bad features across subjects
    keep = [True]*len(g1_data[b][0]) # they all have the same number of features
    for bad in bad_features[b]:
        if len(bad)>0:
            keep[bad] = False
    # print bands[b]
    x = np.array(g1_data[b])#[:,keep]
    y = np.array(g2_data[b])#[:,keep]
    z = np.array(g3_data[b])#[:,keep]
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

