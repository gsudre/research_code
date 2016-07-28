# Grabs the results from SOLAR univariate and bivariate analysis and formats it
# into a nice table.
import os
from math import *
import csv
import glob
home = os.path.expanduser('~')


dir_name = home + '/data/solar_paper_review/'
analysis = 'fmri_nets_mean_GE22'
out_fname = dir_name + 'polygen_results_%s.csv' % analysis

folders = glob.glob(dir_name + analysis + '/*')

header = ['phen', 'h2r', 'h_pval', 'h2r_se', 'c2', 'c2_pval', 'high_kurtosis']

results = [header]

# gather all the traits we used
traits = []
for folder in folders:
    res_dir = folder.split('/')[-1]
    # the trait name is represented by all directories that do not start with
    # one of the bivariate analysis names
    if (res_dir.split('_')[0].find('inatt') < 0 and
       res_dir.split('_')[0].find('hi') < 0 and
       res_dir.split('_')[0].find('total') < 0):
        traits.append(res_dir)

for trait in traits:
    result = [trait]
    # grab the univariate heritability estimates
    folder = dir_name + analysis + '/' + trait
    fname = folder + '/polygenic.out'
    fid = open(fname, 'r')
    c2 = -1
    for line in fid:
        if line.find('H2r is') >= 0:
            h2r = line.split('is ')[-1].split(' ')[0]
            p = line.split('= ')[-1].split(' ')[0]
            result.append(h2r)
            result.append(p)
            # there's no SE when h2r is 0
            if float(h2r) < 0.000000001:
                result.append(0)
        if line.find('C2 is') >= 0:
            c2 = line.split('is ')[-1].split(' ')[0]
            # there's no p-value when c2 = 0
            if float(c2) < 0.000000001:
                p = .5
            else:
                p = line.split('= ')[-1].split(' ')[0]
            result.append(c2)
            result.append(p)
        if line.find('Residual Kurtosis') >= 0:
            if line.find('too high') > 0:
                print 'Residual kurtosis too high for', result[0]
                kurt = 1
            else:
                kurt = 0
            # if we got here but haven't seen any C2, then we didn't calculate
            # it
            if c2 == -1:
                result.append('')
                result.append('')
            result.append(kurt)
        if line.find('H2r Std. Error:') >= 0:
            se = line.split(':')[-1]
            result.append(se)
    fid.close()
    results.append(result)

fout = open(out_fname, 'w')
wr = csv.writer(fout)
wr.writerows(results)
fout.close()
