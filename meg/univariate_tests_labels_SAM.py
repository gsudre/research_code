''' Checks whether there is a group difference in the connectivity '''

import mne
import numpy as np
from scipy import stats
import os
home = os.path.expanduser('~')


band_names = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
bands = range(len(band_names))
g1_fname = '/Users/sudregp/data/meg/nv_subjs.txt'
g2_fname = '/Users/sudregp/data/meg/persistent_subjs.txt'
g3_fname = '/Users/sudregp/data/meg/remitted_subjs.txt'
inatt_fname = '/Users/sudregp/data/meg/inatt.txt'
hi_fname = '/Users/sudregp/data/meg/hi.txt'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = '/Users/sudregp/data/meg/sam/'
cmethod = 5
alpha=.05
fdr = .05  # 0 for none
mean = False
hemi = -1
all2all = False

# list of lists, indicating which ROIs are grouped together, avoiding non-meaningful connections. Set all2all=True if interested in doing each ROI by itself
selected_labels = []
selected_labels = [[10,9,32,24],[23,31,30],[39,40]] #DMN
# selected_labels = [[32,24],[23],[39]] #DMN-select
# selected_labels = [[8], [39, 40, 7]] # dorsal
# selected_labels = [[39,40,41,42], [44,45,46]] #ventral
# selected_labels = [[39], [44,45,46]] #ventral-select
# selected_labels = [[46,9], [8], [44,45,47], [6], [7, 5]] # cognitive control
# selected_labels = [[32,24], [25], [10,11,47]] #affective
selected_labels = [1,10,11,17,18,19,2,20,21,22,23,24,25,3,31,32,37,38,39,4,40,41,42,43,44,45,46,47,5,6,7,8,9] #Hillebrand

if all2all:
    selected_labels = [[roi] for group in selected_labels for roi in group]

def do_test(d1, d2, comp):
    t_threshold = -stats.distributions.t.ppf(alpha / 2., d1.shape[0]+d2.shape[0]-1)
    T_obs, clusters, cluster_p_values, H0 = mne.stats.spatio_temporal_cluster_test([d1, d2], n_jobs=5, threshold=t_threshold, n_permutations=1024, verbose=False)
    good_cluster_inds = np.where(cluster_p_values < fdr)[0]
    print '%s: good clusters: %d'%(comp, len(good_cluster_inds))
    # if len(good_cluster_inds)>0:
    #     vox = np.zeros(nfeats)
    #     vox[delme] = 1
    #     remain = np.nonzero(vox==0)[0]
    #     for i, ind in enumerate(good_cluster_inds):
    #         print '--- Cluster %d (%.2f)---'%(i+1,cluster_p_values[ind])
    #         in_cluster = remain[clusters[ind][1]]

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
print m[cmethod]

fid = open('/Users/sudregp/tmp/u.csv','w')

areas = np.load(home+'/sam/areas.npy')[()]
res = np.load(home+'/sam/rois.npz')
rois = list(res['rois'])
nlabels=len(rois)
if hemi>=0:
    if len(selected_labels)>0:
        brodmann_val = [areas[l][hemi] for l in selected_labels]
    else:
        if hemi==0:
            brodmann_val = rois[1:-1:2]
        else:
            brodmann_val = rois[0:-1:2]
    idx = [rois.index(b) for b in brodmann_val]
    delme = np.setdiff1d(range(nlabels),idx)
    nlabels -= len(delme) 
else:
    if len(selected_labels)>0:
        brodmann_val = [i for l in selected_labels for i in areas[l]]
    else:
        brodmann_val = rois
    idx = [rois.index(b) for b in brodmann_val]
    delme = np.setdiff1d(range(nlabels),idx)
    nlabels -= len(delme) 

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
il = np.tril_indices(nlabels, k=-1)
for s in subjs:
    fname = data_dir + '%s_roi_connectivity.npy'%s
    conn = np.load(fname)[()]
    nbands = len(bands)
    for bidx,bval in enumerate(bands):
        data = conn[bval][cmethod][:,:].squeeze()
        data = np.delete(data, delme, axis=0)
        data = np.delete(data, delme, axis=1) 
        data = data[il]
        if s in g1:
            g1_data[bidx].append(data)
            if bidx==0:
                g1_subjs.append(s)
                # g1_sx.append(sx[s])
        elif s in g2:
            g2_data[bidx].append(data)
            if bidx==0:
                g2_subjs.append(s)
                # g2_sx.append(sx[s])
        elif s in g3:
            g3_data[bidx].append(data)
            if bidx==0:
                g3_subjs.append(s)

inatt = g2_inatt + g3_inatt
hi = g2_hi + g3_hi
score=0
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
            # adhd = np.hstack([y[:, i], z[:,i]])
            # slope, intercept, r_value, pval, std_err = stats.linregress(adhd,inatt)
            # val[8].append(pval)
            # slope, intercept, r_value, pval, std_err = stats.linregress(adhd,hi)
            # val[9].append(pval)
        cnt = 0
        for pvals in val:
            reject_fdr, pval_fdr = mne.stats.fdr_correction(pvals, alpha=fdr, method='indep')
            res.append('%d | %d | %d'%(sum(np.array(pvals)<alpha),sum(np.array(pval_fdr)<fdr), sum(np.array(pvals)<(alpha/nfeats))))
            cnt+=sum(np.array(pvals)<alpha)
        print '\t'.join(str(i) for i in res)
        print cnt
        fid.write(','.join(str(i) for i in res) + ',,')
    else:
        # f, pval = stats.f_oneway(np.nanmean(x,axis=1),np.nanmean(y,axis=1),np.nanmean(z,axis=1))
        # res.append(pval) 
        # f, pval = stats.kruskal(np.nanmean(x,axis=1),np.nanmean(y,axis=1),np.mean(z,axis=1))
        # res.append(pval) 
        # f, pval = stats.ttest_ind(np.nanmean(x,axis=1),np.nanmean(y,axis=1),equal_var=False) 
        # res.append(pval)
        # f, pval = stats.ttest_ind(np.nanmean(x,axis=1),np.nanmean(z,axis=1),equal_var=False) 
        # res.append(pval)
        # f, pval = stats.ttest_ind(np.nanmean(y,axis=1),np.nanmean(z,axis=1),equal_var=False) 
        # res.append(pval)
        f, pval = stats.mannwhitneyu(np.nanmean(x,axis=1),np.nanmean(y,axis=1))
        res.append(2*pval)
        if (res[-1])<.05:
            print '%.2f : %.2f'%(np.nanmean(x),np.nanmean(y))

        f, pval = stats.mannwhitneyu(np.nanmean(x,axis=1),np.nanmean(z,axis=1))
        res.append(2*pval)
        if (res[-1])<.05:
            print '%.2f : %.2f'%(np.nanmean(x),np.nanmean(z))

        f, pval = stats.mannwhitneyu(np.nanmean(y,axis=1),np.nanmean(z,axis=1))
        res.append(2*pval)
        if (res[-1])<.05:
            print '%.2f : %.2f'%(np.nanmean(y),np.nanmean(z))

        adhd = np.hstack([np.nanmean(y,axis=1),np.nanmean(z,axis=1)])
        slope, intercept, r_value, pval, std_err = stats.linregress(adhd,inatt)
        res.append(pval)
        slope, intercept, r_value, pval, std_err = stats.linregress(adhd,hi)
        res.append(pval)
        print ','.join(str(i) for i in res)
        fid.write(','.join(str(i) for i in res) + ',,')
    # score+=cnt
    x = x.reshape((x.shape[0],1,x.shape[1]))
    y = y.reshape((y.shape[0],1,y.shape[1]))
    z = z.reshape((z.shape[0],1,z.shape[1]))
    do_test(x,y,'nvVSper')
    do_test(x,z,'nvVSrem')
    do_test(y,z,'perVSrem')
fid.close()

n1 = len(g1_data[0])
n2 = len(g2_data[0])
n3 = len(g3_data[0])
print 'size1 =', n1
print 'size2 =', n2
print 'size3 =', n3
print score
