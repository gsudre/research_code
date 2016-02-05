import numpy as np
import os
from scipy import stats
import nbs
home = os.path.expanduser('~')

group_names = ['nvs','persistent','remission']
groups_fname = [home+'/data/fmri/joel_%s.txt'%g for g in group_names]
# net = 7
net_names = ['visual','somatomotor','dorsalAttention','ventralAttention',
             'Limbic','frontoParietal','default']
data_folder = home+'/data/results/fmri_Yeo/net%d/'%net
nperms=1000
thresh = [.95, .99, .995, .999]

groups_subjs = []
for fname in groups_fname:
    fid = open(fname, 'r')
    subjs = [line.rstrip() for line in fid]
    fid.close()
    groups_subjs.append(subjs)

fid = open(data_folder+'regionsIn%d_clean.1D'%net, 'r')
rois = [line.rstrip() for line in fid]
fid.close()

# print 'Loading data and computing correlations...'
# corrs = []
# for group in groups_subjs:
#     subj_corrs = []
#     for s in group:
#         subj_data = []
#         for r in rois:
#             data = np.genfromtxt(data_folder+'%s_%sin%d.1D'%(s,r,net))
#             if len(data) > 0:
#                 subj_data.append(data)
#             else:
#                 print "bad data: %s in %s"%(s,r)
#                 subj_data.append([np.nan]*123)
#         subj_corrs.append(np.corrcoef(subj_data))
#     corrs.append(subj_corrs)

nvVSper = []
nvVSrem = []
perVSrem = []
nvVSper_mwu = []
nvVSrem_mwu = []
perVSrem_mwu = []
anova = []
kruskal = []
inatt = []
hi = []

x = np.arctanh(np.array(corrs[0]).transpose([1,2,0]))
y = np.arctanh(np.array(corrs[1]).transpose([1,2,0]))
z = np.arctanh(np.array(corrs[2]).transpose([1,2,0]))
for t in thresh:
    # anova.append(nbs.compute_nbs('anova',x,y,t,nperms,z))
    # kruskal.append(nbs.compute_nbs('kw',x,y,t,nperms,z))
    # nvVSper_mwu.append(nbs.compute_nbs('mwu',x,y,t,nperms))
    # nvVSrem_mwu.append(nbs.compute_nbs('mwu',x,z,t,nperms))
    # perVSrem_mwu.append(nbs.compute_nbs('mwu',y,z,t,nperms))
    nvVSper.append(nbs.compute_nbs('ttest',x,y,t,nperms))
    nvVSrem.append(nbs.compute_nbs('ttest',x,z,t,nperms))
    perVSrem.append(nbs.compute_nbs('ttest',y,z,t,nperms))
    # inatt.append(nbs.compute_nbs('linreg',np.dstack([y, z]),np.array(g2_inatt+g3_inatt),t,nperms))
    # hi.append(nbs.compute_nbs('linreg',np.dstack([y, z]),np.array(g2_hi+g3_hi),t,nperms))

print [r[0] for r in nvVSper]
print [r[0] for r in nvVSrem]
print [r[0] for r in perVSrem]