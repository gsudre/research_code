# Grabs the results from SOLAR univariate and bivariate analysis and formats it into a nice table.
import os
home = os.path.expanduser('~')
from math import *
import csv
import glob
import numpy as np
import pylab as pl


dir_name = home + '/data/solar_paper_v2/'
analysis = 'trait_correlation_small_mean'

folders = glob.glob(dir_name + analysis + '/*')

# figure out all traits we have
traits = [d.split('_AND_')[0].split('/')[-1] for d in folders] + \
         [d.split('_AND_')[1] for d in folders]
traits = np.unique(traits)

# create matrices to store correlations and pvals
ntraits = len(traits)
rhog = np.ones([ntraits, ntraits])
rhop = np.ones([ntraits, ntraits])
rhoe = np.ones([ntraits, ntraits])
rhog_pvals = np.zeros([ntraits, ntraits])
rhoe_pvals = np.zeros([ntraits, ntraits])
for folder in folders:
    # find out the index where to store the values
    t1, t2 = folder.split('_AND_')
    t1 = t1.split('/')[-1]
    i = [k for k in range(ntraits) if traits[k] == t1][0]
    j = [k for k in range(ntraits) if traits[k] == t2][0]

    # collect the results for the bivariate analysis
    fname = folder + '/polygenic.out'
    fid = open(fname, 'r')
    for line in fid:
        if line.find('RhoG is') >= 0:
            rg = float(line.split('is ')[-1].split(' ')[0])
        if line.find('RhoG different from zero') >= 0:
            rgp = line.split('= ')[-1].split(' ')[0]
        if line.find('RhoE is') >= 0:
            re = float(line.split('is ')[-1].split(' ')[0])
            rep = float(line.split('= ')[-1])
        if line.find('Derived Estimate of RhoP') >= 0:
            rp = float(line.split('is ')[-1].split(' ')[0])
    fid.close()
    rhog[i, j] = rg
    rhog[j, i] = rg
    rhog_pvals[i, j] = rgp
    rhog_pvals[j, i] = rgp
    rhoe[i, j] = re
    rhoe[j, i] = re
    rhoe_pvals[i, j] = rep
    rhoe_pvals[j, i] = rep
    rhop[i, j] = rp
    rhop[j, i] = rp


def plot_correlations(corr):
    pl.figure()
    pl.imshow(corr, interpolation='none')
    pl.colorbar()
    pl.xticks(range(corr.shape[1]), traits, rotation='vertical')
    pl.yticks(range(corr.shape[0]), traits)
    pl.show(block=False)
    return pl.gcf


# just for visualization, let's put only DTI as rows, and fMRI as columns
m = np.zeros([33, 24])
m_p = np.zeros_like(m)
fmri_idx = [i for i in range(ntraits) if traits[i].find('net') >= 0]
fmri_names = [traits[i] for i in fmri_idx]
cnt = 0
idx = [i for i in range(ntraits) if traits[i].find('fa') == 0]
dti_names = [traits[i] for i in idx]
for i, j in enumerate(fmri_idx):
    m[cnt:(cnt + len(idx)), i] = rhog[idx, j] 
    m_p[cnt:(cnt + len(idx)), i] = rhog_pvals[idx, j]
cnt += len(idx)
idx = [i for i in range(ntraits) if traits[i].find('ad') == 0]
dti_names += [traits[i] for i in idx]
for i, j in enumerate(fmri_idx):
    m[cnt:(cnt + len(idx)), i] = rhog[idx, j] 
    m_p[cnt:(cnt + len(idx)), i] = rhog_pvals[idx, j]
cnt += len(idx)
idx = [i for i in range(ntraits) if traits[i].find('rd') == 0]
dti_names += [traits[i] for i in idx]
for i, j in enumerate(fmri_idx):
    m[cnt:(cnt + len(idx)), i] = rhog[idx, j] 
    m_p[cnt:(cnt + len(idx)), i] = rhog_pvals[idx, j]


# or we can use just the heritable ones in the split groups:
fa = ['fa_cc', 'fa_left_cst', 'fa_left_ifo', 'fa_left_slf', 'fa_left_unc',
      'fa_right_cst', 'fa_right_ifo', 'fa_right_slf', 'fa_right_unc']
ad = ['ad_cc', 'ad_left_ifo', 'ad_right_cst', 'ad_right_ifo', 'ad_right_slf']
rd = ['rd_cc', 'rd_left_ifo', 'rd_left_slf', 'rd_left_unc', 'rd_right_cst',
      'rd_right_ifo', 'rd_right_ilf', 'rd_right_slf']
fmri = ['net00_pc01', 'net00_pc02', 'net02_pc01', 'net04_pc02', 'net08_pc02']
dti = fa + ad + rd
m = np.zeros([len(dti),len(fmri)])
m_p = np.zeros_like(m)
fmri_idx = [i for i in range(ntraits) if traits[i] in fmri]
fmri_names = [traits[i] for i in fmri_idx]
idx = [i for i in range(ntraits) if traits[i] in dti]
dti_names = [traits[i] for i in idx]
for i, j in enumerate(fmri_idx):
    m[:, i] = rhog[idx, j] 
    m_p[:, i] = rhog_pvals[idx, j]
m_t = m.copy()
m_t[m_p > .05] = np.nan
pl.figure()
pl.imshow(m_t, interpolation='none')
pl.colorbar()
pl.xticks(range(m.shape[1]), fmri_names, rotation='vertical')
pl.yticks(range(m.shape[0]), dti_names)
pl.show(block=False)
aps = stats.fdr_correction(m_p, .05, method='indep')


# how about heritable ones after FDR in the entire set?
fa = ['fa_cc', 'fa_left_cst', 'fa_left_ifo', 'fa_left_slf', 'fa_left_unc',
      'fa_right_cst', 'fa_right_ifo', 'fa_right_slf', 'fa_right_unc']
ad = ['ad_cc', 'ad_left_cst', 'ad_left_ifo', 'ad_left_ilf', 'ad_left_slf',
      'ad_left_unc', 'ad_right_cst', 'ad_right_ifo', 'ad_right_slf']
rd = ['rd_cc', 'rd_left_cst', 'rd_left_ifo', 'rd_left_ilf', 'rd_left_slf',
      'rd_left_unc', 'rd_right_cst', 'rd_right_ifo', 'rd_right_ilf',
      'rd_right_slf']
fmri = ['net00_pc01', 'net00_pc02', 'net02_pc01', 'net04_pc00', 'net04_pc01',
        'net04_pc02', 'net06_pc00', 'net06_pc02', 'net08_pc00', 'net08_pc02',
        'net11_pc00', 'net11_pc01', 'net12_pc02']
dti = fa + ad + rd
m = np.zeros([len(dti),len(fmri)])
m_p = np.zeros_like(m)
fmri_idx = [i for i in range(ntraits) if traits[i] in fmri]
fmri_names = [traits[i] for i in fmri_idx]
idx = [i for i in range(ntraits) if traits[i] in dti]
dti_names = [traits[i] for i in idx]
for i, j in enumerate(fmri_idx):
    m[:, i] = rhog[idx, j] 
    m_p[:, i] = rhog_pvals[idx, j]
m_t = m.copy()
m_t[m_p > .05] = np.nan
pl.figure()
pl.imshow(m_t, interpolation='none')
pl.colorbar()
pl.xticks(range(m.shape[1]), fmri_names, rotation='vertical')
pl.yticks(range(m.shape[0]), dti_names)
pl.show(block=False)
aps = stats.fdr_correction(m_p, .05, method='indep')


# how about within modality, regardless of heritability?
# how about heritable ones after FDR in the entire set?
my_traits = ['cc', 'left_cst', 'left_ifo', 'left_ilf', 'left_slf', 'left_unc',
             'right_cst', 'right_ifo', 'right_ilf', 'right_slf', 'right_unc']
my_traits = ['fa_' + t for t in my_traits]
m = np.zeros([len(my_traits), len(my_traits)])
m_p = np.zeros_like(m)
t_idx = [i for i in range(ntraits) if traits[i] in my_traits]
t_names = [traits[i] for i in t_idx]
for i, j in enumerate(t_idx):
    m[:, i] = rhog[t_idx, j] 
    m_p[:, i] = rhog_pvals[t_idx, j]
m_t = m.copy()
m_t[m_p > .05] = np.nan
pl.figure()
pl.imshow(m_t, interpolation='none')
pl.colorbar()
pl.xticks(range(m.shape[1]), t_names, rotation='vertical')
pl.yticks(range(m.shape[0]), t_names)
pl.show(block=False)
aps = stats.fdr_correction(m_p, .05, method='indep')