''' Checks if connections inside network are different in fMRI.

Gustavo Sudre, 08/2014 '''

import numpy as np
import os
from scipy import stats
import copy
import mne
import nbs
home = os.path.expanduser('~')

def do_tests(x,y,con_titles):
    scores = np.zeros(len(con_titles))
    # # delete features that have inf in them
    # delme = np.nonzero(np.sum(np.isinf(np.vstack([x,y])),axis=0))[0]
    # x = np.delete(x,delme,axis=1)
    # y = np.delete(y,delme,axis=1)
    # for d in delme[::-1]:
    #     con_titles.pop(d)

    print 'T-TESTS'
    pval = stats.ttest_ind(np.mean(x,axis=1),np.mean(y,axis=1),equal_var=equal_var)[1]
    if pval<alpha:
        print 'Brain mean: %.3f'%pval
    pval = stats.ttest_ind(np.mean(x[:,:len(rois)],axis=1),np.mean(y[:,:len(rois)],axis=1),equal_var=equal_var)[1]
    if pval<alpha:
        print 'Left mean: %.3f'%pval
    pval = stats.ttest_ind(np.mean(x[:,len(rois):],axis=1),np.mean(y[:,len(rois):],axis=1),equal_var=equal_var)[1]
    if pval<alpha:
        print 'Right mean: %.3f'%pval
    ps = [stats.ttest_ind(x[:,i],y[:,i],equal_var=equal_var)[1] for i in range(x.shape[1])]
    if min(ps)<alpha:
        print 'All connections:', ' '.join(['%s: %.3f'%(con_titles[p], ps[p]) for p in range(len(ps)) if ps[p]<alpha])
    for i in range(len(ps)):
        if ps[i]<alpha:
            scores[i]+=1

    reject_fdr, pval_fdr = mne.stats.fdr_correction(ps, alpha=alpha, method='indep')
    print 'Surviving FDR:', sum(np.array(pval_fdr)<alpha)
    print 'MWU'
    try: 
        pval = 2*stats.mannwhitneyu(np.mean(x,axis=1),np.mean(y,axis=1))[1]
    except:
        pval=1
    if pval<alpha:
        print 'Brain mean: %.3f'%pval
    try:
        pval = 2*stats.mannwhitneyu(np.mean(x[:,:len(rois)],axis=1),np.mean(y[:,:len(rois)],axis=1))[1]
    except:
        pval=1
    if pval<alpha:
        print 'Left mean: %.3f'%pval
    try:
        pval = 2*stats.mannwhitneyu(np.mean(x[:,len(rois):],axis=1),np.mean(y[:,len(rois):],axis=1))[1]
    except:
        pval=1
    if pval<alpha:
        print 'Right mean: %.3f'%pval
    ps = []
    for i in range(x.shape[1]):
        try:
            pval = 2*stats.mannwhitneyu(x[:,i],y[:,i])[1]
        except:
            pval = 1
        ps.append(pval)
    if min(ps)<alpha:
        print 'All connections:', ' '.join(['%s: %.3f'%(con_titles[p], ps[p]) for p in range(len(ps)) if ps[p]<alpha])
    for i in range(len(ps)):
        if ps[i]<alpha:
            scores[i]+=1
    reject_fdr, pval_fdr = mne.stats.fdr_correction(ps, alpha=alpha, method='indep')
    print 'Surviving FDR:', sum(np.array(pval_fdr)<alpha)
    return scores


hemi = ['lh','rh']
rois = ['brodmannArea24','brodmannArea10','brodmannArea32','brodmannArea39','brodmannArea23','brodmannArea31','brodmannArea40','brodmannArea21','brodmannArea24','brodmannArea9'] #all from Buckner that MEG can see
# rois = ['brodmannArea24','brodmannArea31','brodmannArea39','brodmannArea21','parahippocampal'] # good results, some matching with MEG
# rois = ['brodmannArea24','brodmannArea40','brodmannArea23','brodmannArea21'] # good results, some matching with MEG
# rois = ['brodmannArea24','brodmannArea10','brodmannArea32','brodmannArea29','brodmannArea30','brodmannArea23','brodmannArea31','brodmannArea39','brodmannArea40','brodmannArea21','brodmannArea24','brodmannArea9','hippocampus','parahippocampal'] #all from Buckner
rois = ['brodmannArea10','brodmannArea40','brodmannArea23','brodmannArea21']
data_dir = home+'/data/results/pls_meg_fmri/'
subjs_fname = home+'/data/fmri/steve_all.txt'
g1_fname = home+'/data/fmri/steve_nvs.txt'
g2_fname = home+'/data/fmri/steve_persistent.txt'
g3_fname = home+'/data/fmri/steve_remission.txt'
equal_var=False
alpha=.05
thresh=2.57
nperms=1000
tail='left'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid3 = open(g3_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
g3 = [line.rstrip() for line in fid3]

# create correlations for each subject
il = np.tril_indices(len(rois), k=-1)
g1_data = []
g2_data = []
g3_data = []
for s in subjs:
    subj_data = []
    conn_titles = []
    for h in hemi:
        hemi_data = []
        for r in rois:
            hemi_data.append(np.genfromtxt('%s/%s_%s_%s.1D'%(data_dir,s,r,h)))
        corrs = np.corrcoef(hemi_data)
        subj_data.append(corrs[il])
        conn_titles.append(['%s-%s(%s)'%(rois[il[0][i]],rois[il[1][i]],h) for i in range(len(il[0]))])
    if s in g1:
        g1_data.append(np.array(subj_data).flatten())
    elif s in g2:
        g2_data.append(np.array(subj_data).flatten())
    elif s in g3:
        g3_data.append(np.array(subj_data).flatten())
conn_titles = [i for j in conn_titles for i in j]

g1_data = np.arctanh(g1_data)
g2_data = np.arctanh(g2_data)
g3_data = np.arctanh(g3_data)
print '=== nvVSper ==='
scores = do_tests(g1_data, g2_data, copy.deepcopy(conn_titles))
print '=== nvVSrem ==='
scores += do_tests(g1_data, g3_data, copy.deepcopy(conn_titles))
print '=== remVSper ==='
scores += do_tests(g2_data, g3_data, copy.deepcopy(conn_titles))
# sorted_scores = np.argsort(scores)[::-1]
# for i in sorted_scores:
#     if scores[i]>0:
#         print conn_titles[i],':',scores[i]