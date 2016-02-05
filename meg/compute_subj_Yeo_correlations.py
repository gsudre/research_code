import numpy as np
import os
from scipy import stats
home = os.path.expanduser('~')

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
group_names = ['nv','persistent','remitted']
groups_fname = [home+'/data/meg/%s_subjs.txt'%g for g in group_names]
net = 5
net_names = ['visual','somatomotor','dorsalAttention','ventralAttention',
             'Limbic','frontoParietal','default']
data_folder = home+'/data/results/meg_Yeo/net%d/'%net
inatt_fname = '/Users/sudregp/data/meg/inatt.txt'
hi_fname = '/Users/sudregp/data/meg/hi.txt'

groups_subjs = []
for fname in groups_fname:
    fid = open(fname, 'r')
    subjs = [line.rstrip() for line in fid]
    fid.close()
    groups_subjs.append(subjs)

fid = open(subjs_fname, 'r')
good_subjs = [line.rstrip() for line in fid]
fid.close()

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

band_corrs = []
for band in bands:
    print 'Loading data and computing correlations...', band
    corrs = []
    sx_inatt = []
    sx_hi = []
    for group in groups_subjs:
        subj_corrs = []
        for s in group:
            if s in good_subjs:
                subj_data = []
                for r in rois:
                    data = np.genfromtxt(data_folder+'%s_%sin%d_%d-%d.1D'%(s,r,net,band[0],band[1]))
                    if len(data) > 0:
                        subj_data.append(data)
                    else:
                        print "bad data: %s in %s"%(s,r)
                        subj_data.append([np.nan]*123)
                subj_corrs.append(np.corrcoef(subj_data))

                # constructing symptom lists
                if inatt.has_key(s):
                    sx_inatt.append(inatt[s])
                    sx_hi.append(hi[s])
                else:
                    sx_inatt.append(0)
                    sx_hi.append(0)

        corrs.append(subj_corrs)
    band_corrs.append(corrs)

nrois = len(rois)
il = np.tril_indices(nrois, -1)

# # plot correlation matrix for all groups
# fig = figure()
# cnt=1
# for corrs in band_corrs:
#     mean_corrs = [np.nanmean(m, axis=0) for m in corrs]
#     vmin = np.min([np.nanmin(m) for m in mean_corrs])
#     vmax = np.max([np.nanmax(m) for m in mean_corrs])
#     for gidx, gname in enumerate(group_names):
#         ax = subplot(6, 3, cnt)
#         mappable = ax.imshow(mean_corrs[gidx], interpolation="nearest", vmin=vmin, vmax=vmax)
#         ax.set_title(gname + ': %s (net%d)'%(net_names[net-1],net))
#         axis('tight')
#         cnt += 1

# run t-test and plot 1-pvals
fig = figure()
cnt = 1
for corrs in band_corrs:
    ttest_pvals = []
    combs = [[0,1], [0,2], [1,2]]
    for comb in combs:
        pvals = np.zeros([nrois, nrois])
        for i in range(nrois):
            for j in range(nrois):
                x = np.arctanh([corrs[comb[0]][s][i,j] for s in range(len(corrs[comb[0]]))])
                y = np.arctanh([corrs[comb[1]][s][i,j] for s in range(len(corrs[comb[1]]))])
                tstat, pval = stats.ttest_ind(x[~np.isnan(x)], y[~np.isnan(y)], equal_var=False)
                pvals[i,j] = 1-pval
        ttest_pvals.append(pvals)

    # plotting 1-pvals
    vmin = .95
    vmax = np.max([np.nanmax(m) for m in ttest_pvals])
    if vmax<vmin:
        vmax=vmin
    for cidx, comb in enumerate(combs):
        ax = subplot(6, 3, cnt)
        mappable = ax.imshow(ttest_pvals[cidx], interpolation="nearest", vmin=vmin, vmax=vmax)
        ax.set_title(group_names[comb[0]]+' vs '+group_names[comb[1]]+': %s (net%d)'%(net_names[net-1],net))
        axis('tight')
        cnt += 1
    colorbar(mappable, ax=ax)

# # generating whole matrix t-test. using abs() and mean over all lower triangle connections (does not include diagonal)
# comb_ttests = []
# for cidx in range(len(combs)):
#     mean_tstat = np.nanmean(np.abs(ttests_tstats[cidx][il]))
#     pval = stats.t.sf(np.abs(mean_tstat), len(il[0])-1)*2
#     comb_ttests.append(1-pval)
# print comb_ttests 

# run symptom correlation and plot 1-pvals
fig = figure()
cnt = 1
for corrs in band_corrs:
    linreg_pvals = []
    pvals = np.zeros([nrois, nrois])
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
    if vmax<vmin:
        vmax=vmin
    for cidx in range(len(linreg_pvals)):
        ax = subplot(6, 4, cnt)
        mappable = ax.imshow(linreg_pvals[cidx], interpolation="nearest", vmin=vmin, vmax=vmax)
        ax.set_title(linreg_titles[cidx]+': %s (net%d)'%(net_names[net-1],net))
        axis('tight')
        cnt += 1
    colorbar(mappable, ax=ax)