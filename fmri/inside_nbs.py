''' Checks if connections inside network are different in fMRI.

Gustavo Sudre, 08/2014 '''

import numpy as np
import os
import nbs
home = os.path.expanduser('~')


hemi = ['lh','rh']
rois = ['brodmannArea24','brodmannArea10','brodmannArea32','brodmannArea39','brodmannArea23','brodmannArea31','brodmannArea40','brodmannArea21','brodmannArea24','brodmannArea9'] #all from Buckner that MEG can see
# rois = ['brodmannArea24','brodmannArea31','brodmannArea39','brodmannArea21','parahippocampal'] # good results, some matching with MEG
# rois = ['brodmannArea24','brodmannArea40','brodmannArea23','brodmannArea21'] # good results, some matching with MEG
# rois = ['brodmannArea24','brodmannArea10','brodmannArea32','brodmannArea29','brodmannArea30','brodmannArea23','brodmannArea31','brodmannArea39','brodmannArea40','brodmannArea21','brodmannArea24','brodmannArea9','hippocampus','parahippocampal'] #all from Buckner
# rois = ['brodmannArea10','brodmannArea40','brodmannArea23','brodmannArea21']
data_dir = home+'/data/results/pls_meg_fmri/'
subjs_fname = home+'/data/fmri/steve_all.txt'
g1_fname = home+'/data/fmri/steve_nvs.txt'
g2_fname = home+'/data/fmri/steve_persistent.txt'
g3_fname = home+'/data/fmri/steve_remission.txt'
equal_var=False
alpha=.05
thresh=2.56
nperms=1000
tail='both'
stats='ttest'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
fid2 = open(g2_fname, 'r')
fid3 = open(g3_fname, 'r')
g1 = [line.rstrip() for line in fid1]
g2 = [line.rstrip() for line in fid2]
g3 = [line.rstrip() for line in fid3]

# create correlations for each subject
il = np.tril_indices(2*len(rois), k=-1)
g1_data = []
g2_data = []
g3_data = []
for s in subjs:
    hemi_data = [np.genfromtxt('%s/%s_%s_%s.1D'%(data_dir,s,r,h)) for h in hemi for r in rois]
    corrs = np.corrcoef(hemi_data)
    subj_data = corrs
    headers = ['%s(%s)'%(r,h) for h in hemi for r in rois]
    conn_titles = ['%s - %s'%(headers[il[0][i]],headers[il[1][i]]) for i in range(len(il[0]))]
    if s in g1:
        g1_data.append(np.array(subj_data))
    elif s in g2:
        g2_data.append(np.array(subj_data))
    elif s in g3:
        g3_data.append(np.array(subj_data))

res=[]
g1_data = np.arctanh(g1_data).transpose([1,2,0])
g2_data = np.arctanh(g2_data).transpose([1,2,0])
g3_data = np.arctanh(g3_data).transpose([1,2,0])
print '=== nvVSper ==='
pval, adj, null = nbs.compute_nbs(stats,g1_data,g2_data,thresh,nperms,tail)
res.append([pval,adj])
print '=== nvVSrem ==='
pval, adj, null = nbs.compute_nbs(stats,g1_data,g3_data,thresh,nperms,tail)
res.append([pval,adj])
print '=== remVSper ==='
pval, adj, null = nbs.compute_nbs(stats,g2_data,g3_data,thresh,nperms,tail)
res.append([pval,adj])