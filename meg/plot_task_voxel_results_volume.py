''' Plots the results of the task voxelwise tests'''

import numpy as np
import os
home = os.path.expanduser('~')
import pandas as pd
import nibabel as nb
import pylab as pl
from scipy import stats
import glob
import mne


data_dir = '/mnt/shaw/MEG_data/analysis/stop/source_volume_at_red/nii_tlrc/'
res_dir = '/mnt/shaw/MEG_data/analysis/stop/whole_brain_volume_results/red/'
gf_fname = '/mnt/shaw/MEG_behavioral/gf.csv'
mask_fname = 'hi_DICSevoked_4to8_clean_STI-correct_p0.99a0.05_perms1000.npz'

groups = ['persistent', 'remission', 'NV']
colors = ['r', 'b', 'g']

# load data (will need for time plot)
gf = pd.read_csv(gf_fname)

vox_pos = np.genfromtxt(data_dir + '/mask.txt')
nfeats = vox_pos.shape[0]

params = mask_fname
if params.find('afterZero') >= 0:
    after_zero = True
    params = params.replace('_afterZero', '')
    times = np.arange(0, .94, .05)
else:
    after_zero = False
    times = np.arange(-.5, .94, .05)

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
if clean:
    fmask = '*%s_%s_clean.nii' % (cond, ltype)
else:
    fmask = '*%s_%s.nii' % (cond, ltype)
files = glob.glob(data_dir + fmask)
X = []
gf_loc = []
print 'Loading data...'
for f, fname in enumerate(files):
    print 'File %d / %d' % (f + 1, len(files))
    # exclude due to psychotropic factors
    if fname.find('WCEYBWMO') < 0:
        if ltype.find('DICSepochs') >= 0:
            ntimes = 1
        elif after_zero:
            ntimes = 19
        else:
            ntimes = 29
        img = nb.load(fname)
        subj_data = np.zeros([nfeats, ntimes])
        for i in range(nfeats):
            if img.get_data().ndim > 3:
                subj_data[i, :] = img.get_data()[int(vox_pos[i, 0]),
                                                 int(vox_pos[i, 1]),
                                                 int(vox_pos[i, 2]),
                                                 (img.shape[-1] - ntimes):]
            else:
                subj_data[i, :] = img.get_data()[int(vox_pos[i, 0]),
                                                 int(vox_pos[i, 1]),
                                                 int(vox_pos[i, 2])]
        X.append(subj_data)
        subj = fname.split('/')[-1].split('_')[0]
        gf_loc.append(np.nonzero(gf.maskid == subj)[0][0])
if len(X) != len(gf_loc):
    print 'Mismatch between subject data and gf!'
gf = gf.iloc[gf_loc]

print ntimes

# load the actual result
res = np.load(res_dir + mask_fname)
nclusters = res['clusters'].shape[0]
print 'Found %d clusters.' % nclusters
d = [res['stat_obs'], res['clusters'], res['p_values'], 0]

# this is an adapted version of mne.stats.summarize_clusters_stc. One that doesn't return a surface STC
T_obs, clusters, clu_pvals, _ = d
n_times, n_vertices = T_obs.shape
good_cluster_inds = np.where(clu_pvals < .05)[0]

#  Build a convenient representation of each cluster, where each
#  cluster becomes a "time point" in the SourceEstimate
data = np.zeros((n_vertices, n_times))
data_summary = np.zeros((n_vertices, len(good_cluster_inds) + 1))
for ii, cluster_ind in enumerate(good_cluster_inds):
    data.fill(0)
    v_inds = clusters[cluster_ind][1]
    t_inds = clusters[cluster_ind][0]
    data[v_inds, t_inds] = T_obs[t_inds, v_inds]
    # Store a nice visualization of the cluster by summing across time
    data = np.sign(data) * np.logical_not(data == 0) * (times[1] - times[0])
    data_summary[:, ii + 1] = 1e3 * np.sum(data, axis=1)
    # Make the first "time point" a sum across all clusters for easy
    # visualization
data_summary[:, 0] = np.sum(data_summary, axis=1)

# writing result to .nii file
res = np.zeros(img.get_data().shape[:3] + tuple([data_summary.shape[-1]]))
for i in range(nfeats):
    pos = [int(vox_pos[i, j]) for j in range(3)]
    res[pos[0], pos[1], pos[2], :] = data_summary[i, :]
nii_fname = mask_fname[:-4] + '.nii'
nb.save(nb.Nifti1Image(res, img.get_affine()), res_dir + nii_fname)

# let's make some dataplots now. Start with one data trace per group in the cluster
g0 = [X[i].T for i, group in enumerate(gf.group) if group == groups[0]]
g1 = [X[i].T for i, group in enumerate(gf.group) if group == groups[1]]
g2 = [X[i].T for i, group in enumerate(gf.group) if group == groups[2]]
data = [g0, g1, g2]

fig = pl.figure(figsize=[10.7, 4.5 * nclusters])
cnt = 1
for cl in range(nclusters):
    v_inds = clusters[cl][1]
    t_inds = clusters[cl][0]
    signals = [np.mean(np.mean(np.array(s)[:, :, v_inds], axis=0),
                       axis=1).squeeze() for s in data]
    pl.subplot(nclusters, 2, cnt)
    # The time plot figure only makes sense if it's not DICS_epochs
    if mask_fname.find('DICSepochs') < 0:
        for c in range(len(colors)):
            pl.plot(times, signals[c], color=colors[c])
        pl.xlabel('Time (s)')
        pl.ylabel('Activation')
        pl.legend(groups, loc='best')
        pl.plot([0, 0], pl.ylim(), ':k')
        pl.fill_betweenx(pl.ylim(), times[np.min(t_inds)],
                         times[np.max(t_inds)], color='grey', alpha=0.3)
    cnt += 1

    # now, work on the mean over time barplot or regression, depending on result
    pl.subplot(nclusters, 2, cnt)
    my_test = mask_fname.split('_')[0]
    if my_test.find('anova') >= 0 or my_test.find('nvVSper') >= 0 or \
       my_test.find('nvVSrem') >= 0 or my_test.find('perVSrem') >= 0:
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
