import os
import sys
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import io

home = os.path.expanduser('~')
gf_fname = home + '/data/fmri/gf.csv'
data_dir = home + '/data/fmri_full_grid/rois_spheres/'

if len(sys.argv) > 1:
    ll, ul, res_per_dir = [int(i) for i in sys.argv[1:]]
else:
    ll = 2301500
    ul = 2301600
    res_per_dir = 1000

print 'Loading data'
corr_mats = io.loadmat(data_dir + 'corrs.mat')['corr_mats']
gf = pd.read_csv(gf_fname)
ul = min(ul, corr_mats.shape[1] - 1)
my_conns = range(ll, ul + 1)

print 'Constructing data frame'
col_names = ['maskid'] + ['conn%d' % i for i in range(1, corr_mats.shape[1])]
data = pd.DataFrame(corr_mats, columns=col_names)
print 'Filtering data frame'
cols = ['maskid'] + ['conn%d' % i for i in my_conns]
data = data[cols]
df = pd.merge(gf, data)
df.rename(columns={'age^2': 'age2', 'mvmt^2': 'mvmt2'}, inplace=True)

print 'Starting analysis'
res_mats = np.zeros([df.shape[0], ul - ll + 1])
res_mats[:] = np.nan
for v in range(len(my_conns)):
    conn = 'conn%d' % my_conns[v]
    # print conn
    f = '%s ~ age + C(sex) + mvmt + mvmt2' % conn
    est = smf.ols(formula=f, data=df).fit()
    res_mats[:, v] = est.resid

out_fname = home + '/data/results/tmp/%06d/conn%07dto%07d.txt'
out_fname = out_fname % (ul / res_per_dir, ll, ul)
np.savetxt(out_fname, res_mats)
