''' Run stats tests on PCs of a network '''

import numpy as np
import os
import mne
home = os.path.expanduser('~')
import nibabel as nb
from sklearn.decomposition import PCA
import pandas as pd
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm


z_thresh = 2
p_thresh = .05
comps = [0, 1, 2, 3, 5, 6, 9, 10, 11, 12, 14, 16, 17, 18, 19, 21, 22, 25]
comps = [12, 5, 0, 1, 21, 22]  # z=5
comps = [12, 11, 17, 16, 19, 22]  # z=4
comps = [12, 11, 17, 16, 19, 25]  # z= 2 and 3
comps = [25, 19]
pca_comps = 5
subjs_fname = home+'/data/fmri/joel_all.txt'
data_dir = home + '/data/fmri/ica/dual_regression_alwaysPositive_AllSubjsZeroFilled_scaled/'
ic_fname = home + '/data/fmri/ica/catAllSubjsZeroFilled_aligned_corr0.80_alwaysPositive_avgICmap_zscore.nii'
gf_fname = home + '/data/fmri/gf.csv'


def summarize_results(res, test):
    print '=====', test, '====='
    # correcting for multiple comparisons
    for pc in range(pca_comps):
        ps = np.array([d[:(pc + 1)] for d in res]).flatten()
        reject_bonferroni, pval_bonferroni = mne.stats.bonferroni_correction(ps, alpha=p_thresh/len(ps))
        reject_fdr, pval_fdr = mne.stats.fdr_correction(ps, alpha=p_thresh, method='indep')
        print 'Using %d PCs -> Bonferroni: %d / %d, FDR: %d / %d' % (pc + 1, np.sum(reject_bonferroni), len(ps), np.sum(reject_fdr), len(ps))
    print ''
    # finding good nominal pvalues if we want to resting networks further
    for i, ic in enumerate(res):
        for p, pc in enumerate(ic):
            if pc < p_thresh:
                print 'Nominal p-value: IC %d, PC: %d' % (comps[i], p + 1)
    print '\n'


fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
gf = pd.read_csv(gf_fname)

# the order of subjects in data is the same as in subjs
# let's find that order in the gf and resort it
idx = [np.nonzero(gf.maskid == int(s))[0][0] for s in subjs]
gf = gf.iloc[idx]

mask = nb.load(home + '/data/fmri/downsampled_444/brain_mask_444.nii')
# good voxels
gv = mask.get_data().astype(bool).flatten()
nvoxels = np.sum(gv)

all_anova = []
all_nvVSper = []
all_nvVSrem = []
all_perVSrem = []
all_inatt = []
all_hi = []
all_total = []
all_inattN = []
all_hiN = []
all_totalN = []
for comp in comps:
    data = np.zeros([len(subjs), nvoxels])
    data[:] = np.nan
    print 'Loading data: comp %d' % comp
    for s, subj in enumerate(subjs):
        img = nb.load(data_dir + 'dr_stage2_%s_Z.nii.gz' % subj)
        subj_data = img.get_data()[:, :, :, comp].flatten()
        data[s, :] = subj_data[gv]
    # load the z-scored network map
    img = nb.load(ic_fname)
    ic_data = img.get_data()[:, :, :, comp].flatten()[gv]
    idx = ic_data > z_thresh
    X = data[:, idx]
    pca = PCA(n_components=pca_comps)
    X = pca.fit_transform(X)

    print 'Running tests...'
    col_names = ['pc%d' % i for i in range(pca_comps)]
    # uses the same index so we don't have issues concatenating later
    data_df = pd.DataFrame(X, columns=col_names, index=gf.index, dtype=float)
    df = pd.concat([gf, data_df], axis=1)

    anova = []
    nvVSper = []
    nvVSrem = []
    perVSrem = []
    inatt = []
    hi = []
    total = []
    inattN = []
    hiN = []
    totalN = []
    for v in range(pca_comps):
        keep = np.nonzero(~np.isnan(df['pc%d' % v]))[0]
        est = smf.ols(formula='pc%d ~ group + age + gender' % v, data=df.iloc[keep]).fit()
        an = anova_lm(est)
        anova.append(an['PR(>F)']['group'])

        est = smf.ols(formula='pc%d ~ inatt + age + gender' % v, data=df.iloc[keep]).fit()
        inattN.append(est.pvalues['inatt'])

        est = smf.ols(formula='pc%d ~ hi + age + gender' % v, data=df.iloc[keep]).fit()
        hiN.append(est.pvalues['hi'])

        est = smf.ols(formula='pc%d ~ total + age + gender' % v, data=df.iloc[keep]).fit()
        totalN.append(est.pvalues['total'])

        groups = gf.group.tolist()
        idx = [i for i, g in enumerate(groups)
               if g in ['remission', 'persistent']]
        keep2 = np.intersect1d(keep, idx)
        est = smf.ols(formula='pc%d ~ inatt + age + gender' % v, data=df.iloc[keep2]).fit()
        inatt.append(est.pvalues['inatt'])

        est = smf.ols(formula='pc%d ~ hi + age + gender' % v, data=df.iloc[keep2]).fit()
        hi.append(est.pvalues['hi'])

        est = smf.ols(formula='pc%d ~ total + age + gender' % v, data=df.iloc[keep2]).fit()
        total.append(est.pvalues['total'])

        est = smf.ols(formula='pc%d ~ group + age + gender' % v, data=df.iloc[keep2]).fit()
        # find the coefficient with group term
        sx = [x for x, i in enumerate(est.tvalues.keys()) if i.find('group') == 0]
        if len(sx) > 0:
            sx = sx[0]
            perVSrem.append(est.pvalues[sx])
        else:
            perVSrem.append(1)

        idx = [i for i, g in enumerate(groups) if g in ['NV', 'persistent']]
        keep2 = np.intersect1d(keep, idx)
        est = smf.ols(formula='pc%d ~ group + age + gender' % v, data=df.iloc[keep2]).fit()
        sx = [x for x, i in enumerate(est.tvalues.keys()) if i.find('group') == 0]
        if len(sx) > 0:
            sx = sx[0]
            nvVSper.append(est.pvalues[sx])
        else:
            nvVSper.append(1)

        idx = [i for i, g in enumerate(groups) if g in ['NV', 'remission']]
        keep2 = np.intersect1d(keep, idx)
        est = smf.ols(formula='pc%d ~ group + age + gender' % v, data=df.iloc[keep2]).fit()
        sx = [x for x, i in enumerate(est.tvalues.keys()) if i.find('group') == 0]
        if len(sx) > 0:
            sx = sx[0]
            nvVSrem.append(est.pvalues[sx])
        else:
            nvVSrem.append(1)

        print 'PC%d: ANOVA = %.3f, inatt = %.3f, hi = %.3f, total = %.3f, inattWithNVs = %.3f, hiWithNVs = %.3f, totalWithNVs = %.3f, nvVSper = %.3f, nvVSrem = %.3f, perVSrem = %.3f' % (v + 1, anova[-1], inatt[-1], hi[-1], total[-1], inattN[-1], hi[-1], totalN[-1], nvVSper[-1], nvVSrem[-1], perVSrem[-1])

    all_anova.append(anova)
    all_nvVSper.append(nvVSper)
    all_nvVSrem.append(nvVSrem)
    all_perVSrem.append(perVSrem)
    all_inatt.append(inatt)
    all_hi.append(hi)
    all_total.append(total)
    all_inattN.append(inattN)
    all_hiN.append(hiN)
    all_totalN.append(totalN)

summarize_results(all_anova, 'ANOVA')
summarize_results(all_nvVSper, 'nvVSper')
summarize_results(all_nvVSrem, 'nvVSrem')
summarize_results(all_perVSrem, 'perVSrem')
summarize_results(all_inatt, 'inatt')
summarize_results(all_hi, 'hi')
summarize_results(all_total, 'total')
summarize_results(all_inattN, 'inatt (with NVs)')
summarize_results(all_hiN, 'hi (with NVs)')
summarize_results(all_totalN, 'total (withNVs)')
