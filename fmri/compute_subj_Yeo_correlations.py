import numpy as np
import os
from scipy import stats
home = os.path.expanduser('~')

group_names = ['nvs','persistent','remission']
groups_fname = [home+'/data/fmri/joel_%s.txt'%g for g in group_names]
net = 5
net_names = ['visual','somatomotor','dorsalAttention','ventralAttention',
             'Limbic','frontoParietal','default']
data_folder = home+'/data/results/fmri_Yeo/net%d/'%net
inatt_fname = home+'/data/fmri/inatt.txt'
hi_fname = home+'/data/fmri/hi.txt'

groups_subjs = []
for fname in groups_fname:
    fid = open(fname, 'r')
    subjs = [line.rstrip() for line in fid]
    fid.close()
    groups_subjs.append(subjs)

fid = open(data_folder+'regionsIn%d_15pct.1D'%net, 'r')
rois = [line.rstrip() for line in fid]
fid.close()

res = np.recfromtxt(inatt_fname, delimiter='\t')
inatt = {}
for rec in res:
    inatt[rec[0]] = rec[1]
res = np.recfromtxt(hi_fname, delimiter='\t')
hi = {}
for rec in res:
    hi[rec[0]] = rec[1]

print 'Loading data and computing correlations...'
corrs = []
sx_inatt = []
sx_hi = []
for group in groups_subjs:
    subj_corrs = []
    for s in group:
        subj_data = []
        for r in rois:
            data = np.genfromtxt(data_folder+'%s_%sin%d.1D'%(s,r,net))
            if len(data) > 0:
                subj_data.append(data)
            else:
                print "bad data: %s in %s"%(s,r)
                subj_data.append([np.nan]*123)
        subj_corrs.append(np.corrcoef(subj_data))

        # constructing symptom lists
        if inatt.has_key(int(s)):
            sx_inatt.append(inatt[int(s)])
            sx_hi.append(hi[int(s)])
        else:
            sx_inatt.append(0)
            sx_hi.append(0)

    corrs.append(subj_corrs)

nrois = len(rois)
il = np.tril_indices(nrois, -1)

# # plot correlation matrix for all groups
# mean_corrs = [np.nanmean(m, axis=0) for m in corrs]
# vmin = np.min([np.nanmin(m) for m in mean_corrs])
# vmax = np.max([np.nanmax(m) for m in mean_corrs])
# fig = figure()
# for gidx, gname in enumerate(group_names):
#     ax = subplot(1, 3, gidx+1)
#     mappable = ax.imshow(mean_corrs[gidx], interpolation="nearest", vmin=vmin, vmax=vmax)
#     ax.set_title(gname + ': %s (net%d)'%(net_names[net-1],net))
#     axis('tight')

# run t-test
ttests_pvals = []
ttests_tstats = []
combs = [[0,1], [0,2], [1,2]]
for comb in combs:
    pvals = np.zeros([nrois, nrois])
    tstats = np.zeros([nrois, nrois])
    for i in range(nrois):
        for j in range(nrois):
            x = np.arctanh([corrs[comb[0]][s][i,j] for s in range(len(corrs[comb[0]]))])
            y = np.arctanh([corrs[comb[1]][s][i,j] for s in range(len(corrs[comb[1]]))])
            tstat, pval = stats.ttest_ind(x[~np.isnan(x)], y[~np.isnan(y)], equal_var=False)
            pvals[i,j] = 1-pval
            tstats[i,j] = tstat
    ttests_pvals.append(pvals)
    ttests_tstats.append(tstats)
    print 'Num. < .05: %d / %f, corrected: %d'%(np.sum(pvals>.95),np.sum(pvals>.95)/float(len(pvals.ravel())),np.sum((1-pvals)<(.05/len(il[0]))))

# plotting 1-pvals
vmin = .95
vmax = np.max([np.nanmax(m) for m in ttests_pvals])
fig = figure()
for cidx, comb in enumerate(combs):
    ax = subplot(1, 3, cidx+1)
    mappable = ax.imshow(ttests_pvals[cidx], interpolation="nearest", vmin=vmin, vmax=vmax)
    ax.set_title(group_names[comb[0]]+' vs '+group_names[comb[1]]+': %s (net%d)'%(net_names[net-1],net))
    axis('tight')
colorbar(mappable, ax=ax)

# # generating whole matrix t-test. using abs() and mean over all lower triangle connections (does not include diagonal)
# comb_ttests = []
# for cidx in range(len(combs)):
#     mean_tstat = np.nanmean(np.abs(ttests_tstats[cidx][il]))
#     pval = stats.t.sf(np.abs(mean_tstat), len(il[0])-1)*2
#     comb_ttests.append(1-pval)
# print comb_ttests 

# run symptom correlation and plot 1-pvals
pvals = np.zeros([nrois, nrois])
linreg_pvals = []
for i in range(nrois):
    for j in range(nrois):
        y = [sc[i,j] for gc in corrs for sc in gc]
        pval = stats.linregress(sx_inatt,y)[3]
        pvals[i,j] = 1-pval
linreg_pvals.append(pvals)
pvals = np.zeros([nrois, nrois])
for i in range(nrois):
    for j in range(nrois):
        y = [sc[i,j] for gc in corrs for sc in gc]
        pval = stats.linregress(sx_hi,y)[3]
        pvals[i,j] = 1-pval
linreg_pvals.append(pvals)
pvals = np.zeros([nrois, nrois])
for i in range(nrois):
    for j in range(nrois):
        y = [sc[i,j] for gc in corrs[1:] for sc in gc]
        pval = stats.linregress(sx_inatt[len(corrs[0]):],y)[3]
        pvals[i,j] = 1-pval
linreg_pvals.append(pvals)
pvals = np.zeros([nrois, nrois])
for i in range(nrois):
    for j in range(nrois):
        y = [sc[i,j] for gc in corrs[1:] for sc in gc]
        pval = stats.linregress(sx_hi[len(corrs[0]):],y)[3]
        pvals[i,j] = 1-pval
linreg_pvals.append(pvals)

linreg_titles = ['inatt_all','hi_all','inatt_noNVs','hi_noNVs']
vmin = .95
vmax = np.max([np.nanmax(m) for m in linreg_pvals])
fig = figure()
for cidx in range(len(linreg_pvals)):
    ax = subplot(2, 2, cidx+1)
    mappable = ax.imshow(linreg_pvals[cidx], interpolation="nearest", vmin=vmin, vmax=vmax)
    ax.set_title(linreg_titles[cidx]+': %s (net%d)'%(net_names[net-1],net))
    axis('tight')
colorbar(mappable, ax=ax)