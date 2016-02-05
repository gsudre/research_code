''' Plots the results of the task voxelwise tests'''

import numpy as np
import os
home = os.path.expanduser('~')
import pandas as pd
import pylab as pl
from scipy import stats
import glob
import mne


data_dir = '/Volumes/Shaw/MEG_data/analysis/stop/source_surface_at_red/'

res_dir = '/Volumes/Shaw/MEG_data/analysis/stop/new_results/stop_sources_surface_at_red/'

gf_fname = '/Volumes/Shaw/MEG_behavioral/gf.csv'
mask_fname = 'total_DICSepochs_8to13_STI-incorrect_p0.99a0.05_perms1000.npz'

groups = ['persistent', 'remission', 'NV']
colors = ['r', 'b', 'g']

# load data (will need for time plot)
gf = pd.read_csv(gf_fname)

params = mask_fname
if params.find('afterZero') >= 0:
    after_zero = True
    params = params.replace('_afterZero', '')
else:
    after_zero = False

if params.find('clean') >= 0:
    clean = True
    params = params.replace('_clean', '')
else:
    clean = False

cond = params.split('_')[-3]
ltype = '_'.join(params.split('_')[1:3])
print cond
print ltype

print 'Listing all data files...'
files = glob.glob(data_dir + '*%s_%s-lh.stc' % (cond, ltype))
X = []
gf_loc = []
print 'Loading data...'
for f, fname in enumerate(files):
    print 'File %d / %d' % (f, len(files))
    # exclude due to psychotropic factors
    if fname.find('WCEYBWMO') < 0:
        stc = mne.read_source_estimate(fname[:-7])
        if after_zero:
            stc.crop(tmin=0)
        X.append(stc.data)
        subj = fname.split('/')[-1].split('_')[0]
        gf_loc.append(np.nonzero(gf.maskid == subj)[0][0])
if len(X) != len(gf_loc):
    print 'Mismatch between subject data and gf!'
gf = gf.iloc[gf_loc]

# load the actual result
res = np.load(res_dir + mask_fname)
nclusters = res['clusters'].shape[0]
print 'Found %d clusters.' % nclusters
d = [res['stat_obs'], res['clusters'], res['p_values'], 0]
stc_res = mne.stats.summarize_clusters_stc(d, tstep=stc.tstep, subject='fsaverage', tmin=stc.tmin)
if mask_fname.find('DICSepochs') >= 0:
    # DICS_epochs only has one time point, so we need to plot it differently
    brain = stc_res.plot('fsaverage2', 'inflated', 'both',
                         time_label='Significant vertices',
                         clim={'kind': 'value', 'pos_lims': [0, .5, 1]})
else:
    brain = stc_res.plot('fsaverage2', 'inflated', 'both', clim='auto',
                         time_label='Duration significant (ms)')

# let's make some dataplots now. Start with one data trace per group in the cluster
g0 = [X[i].T for i, group in enumerate(gf.group) if group == groups[0]]
g1 = [X[i].T for i, group in enumerate(gf.group) if group == groups[1]]
g2 = [X[i].T for i, group in enumerate(gf.group) if group == groups[2]]
data = [g0, g1, g2]

fig = pl.figure(figsize=[10.7, 4.5 * nclusters])
cnt = 1
for cl in range(nclusters):
    v_inds = res['clusters'][cl][1]
    t_inds = res['clusters'][cl][0]
    signals = [np.mean(np.mean(np.array(s)[:, :, v_inds], axis=0),
                       axis=1).squeeze() for s in data]
    pl.subplot(nclusters, 2, cnt)
    # The time plot figure only makes sense if it's not DICS_epochs
    if mask_fname.find('DICSepochs') < 0:
        for c in range(len(colors)):
            pl.plot(stc.times, signals[c], color=colors[c])
        pl.xlabel('Time (s)')
        pl.ylabel('Activation')
        pl.legend(groups, loc='best')
        pl.plot([0, 0], pl.ylim(), ':k')
        pl.fill_betweenx(pl.ylim(), stc.times[np.min(t_inds)],
                         stc.times[np.max(t_inds)], color='grey', alpha=0.3)
    cnt += 1

    # now, work on the mean over time barplot or regression, depending on result
    pl.subplot(nclusters, 2, cnt)
    my_test = mask_fname.split('_')[0]
    if my_test.find('anova') >= 0 or my_test.find('VS') > 0:
        signals = [np.mean(np.array(s)[:, :, v_inds], axis=2) for s in data]
        signals = [np.mean(s[:, t_inds], axis=1) for s in signals]
        ybars = [np.mean(s) for s in signals]
        y_sd = [np.std(s)/np.sqrt(len(s)) for s in signals]
        pl.bar(np.arange(len(ybars)), ybars, 0.35, color=colors,
               ecolor='k', yerr=y_sd, align='center')
        pl.xticks(range(len(groups)), groups)
        pl.xlim([-.2, 2.5])
        # running post-hoc tests
        print 'cluster %d' % cl + ': nvVSper = %.3f' % stats.ttest_ind(signals[groups.index('NV')], signals[groups.index('persistent')])[1]
        print 'cluster %d' % cl + ': nvVSrem = %.3f' % stats.ttest_ind(signals[groups.index('NV')], signals[groups.index('remission')])[1]
        print 'cluster %d' % cl + ': perVSrem = %.3f' % stats.ttest_ind(signals[groups.index('persistent')], signals[groups.index('remission')])[1]
        f, p = stats.f_oneway(signals[0], signals[1], signals[2])
        print 'ANOVA: F(%d,%d)=%.2f, p=%.g\n' % (len(groups) - 1,
                                                 len(X) - len(groups),
                                                 f, p)
    else:
        # need to make a correlation plot
        if mask_fname.find('NV') > 0:
            sx = mask_fname.split('With')[0]
            x = list(gf[sx])
            y = [np.mean(X[i].T[t_inds, v_inds]) for i in range(gf.shape[0])]
        else:
            sx = mask_fname.split('_')[0]
            x = [gf[sx].iloc[i] for i in range(gf.shape[0]) if gf['group'].iloc[i] in ['persistent', 'remission']]
            y = [np.mean(X[i].T[t_inds, v_inds]) for i in range(gf.shape[0]) if gf['group'].iloc[i] in ['persistent', 'remission']]
        pl.plot(x, y, '.b', ms=10)
        slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
        line = slope * np.array(x) + intercept
        pl.plot(x, line, 'r-', linewidth=5)
        pl.title('r = %.2f, p < %.2f' % (r_value, p_value))
        pl.xlabel(sx)
        pl.ylabel('correlation')
        ax = pl.gca()
        ax.yaxis.labelpad = -5
        pl.axis('tight')
    cnt += 1

pl.suptitle(mask_fname)
