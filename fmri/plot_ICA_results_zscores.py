# creates barplot or scatterplot for meg+fMRI results
import os
from scipy import stats
import numpy as np
import pandas as pd
import nibabel as nb
import pylab as pl
import sys
home = os.path.expanduser('~')


if len(sys.argv) > 1 and sys.argv[1].find('pylab') < 0:
    res_fname = sys.argv[1]
    quiet = bool(sys.argv[2])
else:
    res_fname = 'clustmaskInNet_p95a95Corr_inattAgeGender_inNet_IC23_drStage2Z.nii'
    quiet = False

data_dir = home + '/data/fmri_example11/ica/dual_regression/'
res_dir = home + '/data/fmri_example11/ica/results_zscore/'
net_mask = home + '/data/fmri_example11/brain_mask_444.nii'
# net_mask = res_dir + 'IC10_binNetMask_p01BF.nii'

# open fMRI data
subjs_fname = home + '/data/fmri_example11/all.txt'
gf_fname = home + '/data/fmri_example11/gf.csv'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
gf = pd.read_csv(gf_fname)

# the order of subjects in data is the same as in subjs
# let's find that order in the gf and resort it
idx = [np.nonzero(gf.maskid == int(s))[0][0] for s in subjs]
gf = gf.iloc[idx]

if res_fname.find('total') >= 0:
    all_sx = gf.total.tolist()
elif res_fname.find('inatt') >= 0:
    all_sx = gf.inatt.tolist()
elif res_fname.find('hi') >= 0:
    all_sx = gf.hi.tolist()
else:
    all_sx = gf.total.tolist()

mask = nb.load(res_dir + res_fname)
cl_values = np.unique(mask.get_data())[1:]  # remove 0
nclusters = max(cl_values)

nets = nb.load(net_mask)

my_groups = list(np.unique(gf.group))
groups = gf.group.tolist()

data = []  # list of data per cluster
if not quiet:
    print 'Loading data'
ic = res_fname.split('IC')[-1][:2]
for c in range(nclusters):
    sx = [[] for g in my_groups]  # one list per group
    cl_data = [[] for g in my_groups]  # one list per group
    gv = mask.get_data() == cl_values[c]  # voxels showing the result

    # get voxels showing the result and also inside the network mask
    res_net = np.multiply(gv, nets.get_data()[:, :, :] > 0)
    nvoxels = np.sum(res_net)/float(np.sum(gv))
    if not quiet:
        print 'Cluster %d overlap: %.2f' % (c, nvoxels)

    for sidx, s in enumerate(subjs):
        fname = '%s/dr_stage2_%s_Z.nii.gz' % (data_dir, s)
        img = nb.load(fname)
        subj_data = img.get_data()[gv, int(ic)]
        # # if we want to only plot results inside the network
        # subj_data = img.get_data()[res_net == 1, int(ic)]
        gidx = my_groups.index(groups[sidx])
        cl_data[gidx].append(float(np.nanmean(subj_data)))
        sx[gidx].append(float(all_sx[sidx]))
    data.append(cl_data)


nrows = nclusters
ncols = 2
cnt = 1
fig = pl.figure(figsize=[10.25, nclusters*5.9])

# for each cluster, make a scatterplot and a barplot
for cl in range(nclusters):
    if res_fname.find('NV') > 0:
        x = [i for g in sx for i in g]
        y = [i for g in data[cl] for i in g]
    else:
        x = [i for k, g in enumerate(sx) if my_groups[k] in ['persistent', 'remission'] for i in g]
        y = [i for k, g in enumerate(data[cl]) if my_groups[k] in ['persistent', 'remission'] for i in g]

    slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
    if not quiet:
        pl.subplot(nrows, ncols, cnt)
        # make the scatterplot first
        pl.plot(x, y, '.b', ms=10)
        line = slope * np.array(x) + intercept
        pl.plot(x, line, 'r-', linewidth=5)
        pl.title('r = %.2f, p < %.2f, cluster %d' % (r_value, p_value, cl + 1))
        pl.xlabel('symptoms')
        pl.ylabel('zscores')
        ax = pl.gca()
        ax.yaxis.labelpad = -5
        pl.axis('tight')
        cnt += 1

        # now do the barplot
        pl.subplot(nrows, ncols, cnt)
        ybars = [np.mean(data[cl][i]) for i in range(len(my_groups))]
        y_sd = [np.std(data[cl][i])/np.sqrt(len(sx[i])) for i in range(len(my_groups))]
        pl.bar(np.arange(len(ybars)), ybars, 0.35, color=['g', 'r', 'b'],
               ecolor='k', yerr=y_sd)
        pl.xticks(range(len(my_groups)), ['NV', 'persistent', 'remission'])
        # pl.title(res_fname.split('/')[-1])
        # pl.title()
        pl.xlim([-.2, 2.5])
        cnt += 1

    # do some ttests
    out_str = []
    t, p = stats.ttest_ind(data[cl][0], data[cl][1])
    if t > 0:
        out_str.append('>')
    else:
        out_str.append('<')
    if p < .05:
        out_str[-1] += 's'
    if not quiet:
        print 'fMRI, cluster %d' % cl + ': nvVSper = %.3f' % p
    t, p = stats.ttest_ind(data[cl][0], data[cl][2])
    if t > 0:
        out_str.append('>')
    else:
        out_str.append('<')
    if p < .05:
        out_str[-1] += 's'
    if not quiet:
        print 'fMRI, cluster %d' % cl + ': nvVSrem = %.3f' % p
    t, p = stats.ttest_ind(data[cl][1], data[cl][2])
    if t > 0:
        out_str.append('>')
    else:
        out_str.append('<')
    if p < .05:
        out_str[-1] += 's'
    if not quiet:
        print 'fMRI, cluster %d' % cl + ': perVSrem = %.3f' % p
    f, p = stats.f_oneway(data[cl][0], data[cl][1], data[cl][2])
    if p < .05:
        out_str.append('1')
    else:
        out_str.append('0')
    if not quiet:
        print 'ANOVA: F(%d,%d)=%.2f, p=%.g\n' % (len(data[cl]) - 1,
                                                 len(subjs) - len(data[cl]),
                                                 f,
                                                 p)
    pl.title('ANOVA: F(%d,%d)=%.2f, p=%.g' % (len(data[cl]) - 1,
                                                 len(subjs) - len(data[cl]),
                                                 f,
                                                 p))
    print '\t'.join(out_str)
