# Grabs the results from SOLAR bivariate analysis and formats it into tables.
import os
from math import *
import csv
import glob
import numpy as np
import pylab as pl
import pandas as pd
import sys


home = os.path.expanduser('~')
dir_name = home + '/data/heritability_change/'
analysis = sys.argv[1]

folders = glob.glob(dir_name + analysis + '/*')

# figure out all traits we have
traits_from = np.unique([d.split('_AND_')[0].split('/')[-1] for d in folders])
traits_to = np.unique([d.split('_AND_')[1] for d in folders])

# create matrices to store correlations and pvals
rhog = pd.DataFrame(np.nan, columns=traits_from, index=traits_to)
rhop = pd.DataFrame(np.nan, columns=traits_from, index=traits_to)
rhoe = pd.DataFrame(np.nan, columns=traits_from, index=traits_to)
rhog_pvals = pd.DataFrame(np.nan, columns=traits_from, index=traits_to)
rhoe_pvals = pd.DataFrame(np.nan, columns=traits_from, index=traits_to)
for folder in folders:
    # find out the position where to store the values
    t1, t2 = folder.split('_AND_')
    t1 = t1.split('/')[-1]

    # collect the results for the bivariate analysis
    fname = folder + '/polygenic.out'
    fid = open(fname, 'r')
    for line in fid:
        if line.find('RhoG is') >= 0:
            rhog[t1][t2] = float(line.split('is ')[-1].split(' ')[0])
        if line.find('RhoG different from zero') >= 0:
            rhog_pvals[t1][t2] = line.split('= ')[-1].split(' ')[0]
        if line.find('RhoE is') >= 0:
            rhoe[t1][t2] = float(line.split('is ')[-1].split(' ')[0])
            rhoe_pvals[t1][t2] = float(line.split('= ')[-1])
        if line.find('Derived Estimate of RhoP') >= 0:
            rhop[t1][t2] = float(line.split('is ')[-1].split(' ')[0])
    fid.close()

rhog.to_csv('%s/%s_rhog.csv' % (dir_name, analysis))
rhoe.to_csv('%s/%s_rhoe.csv' % (dir_name, analysis))
rhop.to_csv('%s/%s_rhop.csv' % (dir_name, analysis))
rhog_pvals.to_csv('%s/%s_rhog_pvals.csv' % (dir_name, analysis))
rhoe_pvals.to_csv('%s/%s_rhoe_pvals.csv' % (dir_name, analysis))
