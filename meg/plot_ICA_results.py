''' Checks whether there is a difference in the seed connectivity using OLS with covariates '''

import numpy as np
import os
home = os.path.expanduser('~')
import pandas as pd
import nibabel as nb
import pylab as pl
from scipy import stats


gf_fname = home + '/data/meg/gf.csv'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = home + '/data/meg/ica/'
mask_fname = data_dir + 'results_correlation/clustmaskAllBands_p99a99Corr_totalAgeGender_65-100_IC00.nii'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
gf = pd.read_csv(gf_fname)

mask = nb.load(mask_fname)
# mask = nb.load(data_dir + 'results_correlation/tmp_mask.nii')
cl_values = np.unique(mask.get_data())[1:]  # remove 0
nclusters = max(cl_values)

# the order of subjects in data is the same as in subjs
# let's find that order in the gf and resort it
idx = [np.nonzero(gf.maskid == s)[0][0] for s in subjs]
gf = gf.iloc[idx]

my_groups = list(np.unique(gf.group))
groups = gf.group.tolist()

if mask_fname.find('total') >= 0:
    all_sx = gf.total.tolist()
elif mask_fname.find('inatt') >= 0:
    all_sx = gf.inatt.tolist()
elif mask_fname.find('hi') >= 0:
    all_sx = gf.hi.tolist()
else:
    all_sx = gf.total.tolist()

data = []  # list of data per cluster
std_data = []  # list of data per cluster
print 'Loading data'
freq_band = mask_fname.split('_')[-2]
ic = mask_fname.split('IC')[-1][:2]
for c in range(nclusters):
    sx = [[] for g in my_groups]  # one list per group
    cl_data = [[] for g in my_groups]  # one list per group
    s_data = [[] for g in my_groups]  # one list per group
    gv = mask.get_data() == cl_values[c]
    for sidx, s in enumerate(subjs):
        fname = '%s/%s_%s_alwaysPositive_IC%s.nii' % (data_dir, s, freq_band, ic)
        img = nb.load(fname)
        subj_data = img.get_data()[gv, 0]  # load beta coefficients
        subj_data = img.get_data()[gv, 2]  # load correlation
        gidx = my_groups.index(groups[sidx])
        cl_data[gidx].append(float(np.nanmean(subj_data)))
        s_data[gidx].append(float(np.nanmean(img.get_data()[gv, 4])))
        sx[gidx].append(float(all_sx[sidx]))
    data.append(cl_data)
    std_data.append(s_data)

nrows = nclusters
ncols = 4
cnt = 1
fig = pl.figure(figsize=[17.6, nclusters*4.25])

# for each cluster, make a scatterplot and a barplot
for cl in range(nclusters):
    if mask_fname.find('NV') > 0:
        x = [i for g in sx for i in g]
        y = [i for g in data[cl] for i in g]
    else:
        x = [i for k, g in enumerate(sx) if my_groups[k] in ['persistent', 'remission'] for i in g]
        y = [i for k, g in enumerate(data[cl]) if my_groups[k] in ['persistent', 'remission'] for i in g]

    pl.subplot(nrows, ncols, cnt)
    # make the scatterplot first
    pl.plot(x, y, '.b', ms=10)
    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    line = slope * np.array(x) + intercept
    pl.plot(x, line, 'r-', linewidth=5)
    pl.title('r = %.2f, p < %.2f, cluster %d' % (r_value, p_value, cl + 1))
    pl.xlabel('symptoms')
    pl.ylabel('correlation')
    ax = pl.gca()
    ax.yaxis.labelpad = -5
    pl.axis('tight')
    cnt += 1

    # now do the barplot
    pl.subplot(nrows, ncols, cnt)
    ybars = [np.nanmean(data[cl][i]) for i in range(len(my_groups))]
    y_sd = [np.nanstd(data[cl][i])/np.sqrt(len(sx[i])) for i in range(len(my_groups))]
    pl.bar(np.arange(len(ybars)), ybars, 0.35, color=['g', 'r', 'b'],
           ecolor='k', yerr=y_sd)
    pl.xticks(range(len(my_groups)), ['NV', 'persistent', 'remission'])
    pl.xlim([-.2, 2.5])
    cnt += 1

    # some boxplots
    pl.subplot(nrows, ncols, cnt)
    pl.boxplot(data[cl])
    pl.xticks([1, 2, 3], ['NV', 'persistent', 'remission'])
    pl.title(mask_fname.split('/')[-1])
    cnt += 1

    # bar plots for STD
    pl.subplot(nrows, ncols, cnt)
    ybars = [np.nanmean(std_data[cl][i]) for i in range(len(my_groups))]
    y_sd = [np.nanstd(std_data[cl][i])/np.sqrt(len(sx[i])) for i in range(len(my_groups))]
    pl.bar(np.arange(len(ybars)), ybars, 0.35, color=['g', 'r', 'b'],
           ecolor='k', yerr=y_sd)
    pl.xticks(range(len(my_groups)), ['NV', 'persistent', 'remission'])
    pl.xlim([-.2, 2.5])

    # do some ttests
    print 'Beta tests'
    print 'MEG, cluster %d' % cl + ': nvVSper = %.3f' % stats.ttest_ind(data[cl][0], data[cl][1])[1]
    print 'MEG, cluster %d' % cl + ': nvVSrem = %.3f' % stats.ttest_ind(data[cl][0], data[cl][2])[1]
    print 'MEG, cluster %d' % cl + ': perVSrem = %.3f' % stats.ttest_ind(data[cl][1], data[cl][2])[1]
    f, p = stats.f_oneway(data[cl][0], data[cl][1], data[cl][2])
    print 'ANOVA: F(%d,%d)=%.2f, p=%.g\n' % (len(data[cl]) - 1,
                                             len(subjs) - len(data[cl]),
                                             f,
                                             p)
    print 'STD tests'
    print 'MEG, cluster %d' % cl + ': nvVSper = %.3f' % stats.ttest_ind(std_data[cl][0], std_data[cl][1])[1]
    print 'MEG, cluster %d' % cl + ': nvVSrem = %.3f' % stats.ttest_ind(std_data[cl][0], std_data[cl][2])[1]
    print 'MEG, cluster %d' % cl + ': perVSrem = %.3f' % stats.ttest_ind(std_data[cl][1], std_data[cl][2])[1]

    print '\n\n'


    cnt += 1
