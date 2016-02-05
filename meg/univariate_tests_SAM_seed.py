''' Checks whether there is a group difference in the seed connectivity '''

import mne
import numpy as np
from scipy import stats
import os
home = os.path.expanduser('~')


def write2afni(vals, fname):
    data = np.genfromtxt(home+'/sam/voxelsInROIs.txt', delimiter=' ')
    # only keep i,j,k and one column for data
    data[:,3:] = 0
    for i, d in enumerate(vals):
        data[:,3+i] = d
    np.savetxt(fname, data, fmt='%.2f', delimiter=' ', newline='\n')
    os.system('cat '+fname+ ' | 3dUndump -master '+home+'/sam/TTatlas555+tlrc -ijk -datum float -prefix '+fname+' -overwrite -')

def count_good_sources(voxels, num_print):
    areas = np.load(home+'/sam/areas.npy')[()]
    res = np.load(home+'/sam/rois.npz')
    rois = list(res['rois'])
    roi_voxels = list(res['roi_voxels'])
    roi_score = np.zeros([len(rois)])
    for idx, vox in enumerate(roi_voxels):
        for v in voxels:
            if v in vox:
                roi_score[idx] += 1
    best_rois = np.argsort(-roi_score)[:num_print]
    for r in best_rois:
        if rois[r]==151:
            roi_name='Putamen'
            hemi=1
        elif rois[r]==135:
            roi_name='VentralLateralNucleus'
            hemi=1
        elif rois[r]==351:
            roi_name='Putamen'
            hemi=0
        else:
            ba = [key for key, val in areas.iteritems() if rois[r] in val][0]
            hemi = areas[ba].index(rois[r])
            roi_name = 'BA%d'%ba
        print '%s-%d: %d sources, %.2f of ROI, %.2f of significant sources'%(roi_name, hemi, roi_score[r], roi_score[r]/len(roi_voxels[r]), roi_score[r]/len(voxels))


bands = [[1, 4], [4, 8], [8, 13], [13, 30]]#, [30, 50]]
g1_fname = '/Users/sudregp/data/meg/nv_subjs.txt'
g2_fname = '/Users/sudregp/data/meg/persistent_subjs.txt'
g3_fname = '/Users/sudregp/data/meg/remitted_subjs.txt'
inatt_fname = '/Users/sudregp/data/meg/inatt.txt'
hi_fname = '/Users/sudregp/data/meg/hi.txt'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = '/Users/sudregp/data/meg/sam/seed/'
alpha=.05
fdr = .1  # 0 for none
seed = [1, -44, 3]
seed_name = 'mPFC'
# seed = [ -14, 55, 25]
# seed_name = 'pCC'
# seed = [-8, -1, 38]
# seed_name = 'dACC'
# seed = [-46, -16, 5]
# seed_name = 'rIFG'
# seed = [-32, -40, 27]
# seed_name = 'rMFG' 

coord = np.genfromtxt(home + '/sam/targetsInTLR.txt', delimiter=' ', skip_header=1)
dist = np.sqrt((coord[:,0] - seed[0])**2 + (coord[:,1] - seed[1])**2 + (coord[:,2] - seed[2])**2)
seed_src = np.argmin(dist)
print 'Seed src: %d, Distance to seed: %.2fmm'%(seed_src, np.min(dist))

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

fid = open('/Users/sudregp/tmp/u.csv','w')

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
    fname = data_dir + '%s_%s_connectivity.npy'%(s,seed_name)
    conn = np.load(fname)[()]
    for b in range(len(bands)):
        data = conn[:,b]
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
score=0
for b in range(len(bands)):
    print bands[b]
    X = np.array(g1_data[b])
    Y = np.array(g2_data[b])
    Z = np.array(g3_data[b])
    res = []
    nfeats = X.shape[1]
    print nfeats, 'connections'
    print seed
    val = [[] for i in range(10)]
    for i in range(nfeats):
        if i==seed_src:
            for v in val:
                v.append(np.nan)
        else:
            # get rid of all the NaNs so the nonparametric tests don't get confused
            x = X[~np.isnan(X[:,i]), i]
            y = Y[~np.isnan(Y[:,i]), i]
            z = Z[~np.isnan(Z[:,i]), i]
            f, pval = stats.f_oneway(x,y,z) 
            val[0].append(pval)
            if len(x)>20 and len(y)>20 and len(z)>20:
                f, pval = stats.kruskal(x,y,z) 
            else:
                pval = np.nan
            val[1].append(pval)
            f, pval = stats.ttest_ind(x,y) 
            val[2].append(pval)
            f, pval = stats.ttest_ind(x,z) 
            val[3].append(pval)
            f, pval = stats.ttest_ind(y,z) 
            val[4].append(pval)
            if len(x)>20 and len(y)>20:
                f, pval = stats.mannwhitneyu(x,y) 
            else:
                pval = np.nan
            val[5].append(2*pval)
            if len(x)>20 and len(z)>20:
                f, pval = stats.mannwhitneyu(x,z) 
            else:
                pval = np.nan
            val[6].append(2*pval)
            if len(y)>20 and len(z)>20:
                f, pval = stats.mannwhitneyu(y,z) 
            else:
                pval = np.nan
            val[7].append(2*pval)
            # adhd = np.hstack([y, z])
            # slope, intercept, r_value, pval, std_err = stats.linregress(adhd,inatt)
            # val[8].append(pval)
            # slope, intercept, r_value, pval, std_err = stats.linregress(adhd,hi)
            # val[9].append(pval)
    for pidx, pvals in enumerate(val):
        # we only send in the non-NaN pvals
        keep_me = ~np.isnan(pvals)
        reject_fdr, pval_fdr = mne.stats.fdr_correction(np.array(pvals)[keep_me], alpha=fdr, method='indep')
        res.append('%d | %d\t'%(sum(np.array(pvals)<alpha),sum(np.array(pval_fdr)<fdr)))
        if pidx==5:
            fname='nvVSper'
            mymean = np.nanmean(x,axis=0)-np.nanmean(y,axis=0)
        elif pidx==6:
            fname='nvVSrem'
            mymean = np.nanmean(x,axis=0)-np.nanmean(z,axis=0)
        elif pidx==7:
            fname='perVSrem'
            mymean = np.nanmean(y,axis=0)-np.nanmean(z,axis=0)
        vox = np.zeros_like(np.array(pvals))
        vox[keep_me] = reject_fdr
        if sum(reject_fdr)>0:
            print '--- val %d ---'%pidx
            count_good_sources(np.nonzero(reject_fdr)[0], 5)
    print '\t'.join(str(i) for i in res)
    fid.write(','.join(str(i) for i in res) + ',,')

fid.close()

n1 = len(g1_data[0])
n2 = len(g2_data[0])
n3 = len(g3_data[0])
print 'size1 =', n1
print 'size2 =', n2
print 'size3 =', n3
print score
