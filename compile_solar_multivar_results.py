# Grabs the results from SOLAR univariate analysis and formats it
# into a nice table. These results come from analysis where we run separate
# SOLAR calls, generating one polygenic.out file per trait.
import os
import sys
from math import *
import csv
import glob
home = os.path.expanduser('~')

analysis = sys.argv[1]

dir_name = home + '/data/tmp/'
out_fname = dir_name + 'polygen_results_%s.csv' % analysis

files = glob.glob(dir_name + analysis + '/*polygenic.out')
files.sort()

header = ['phen', 'n', 'h2r', 'h_pval', 'h2r_se', 'c2', 'c2_pval', 'high_kurtosis']

results = [header]

# gather all the traits we used
for fname in files:
    res_file = fname.split('/')[-1]
    trait = res_file.replace('_polygenic.out', '')
#    print('Parsing %s' % trait)

    result = [trait]
    # grab the univariate heritability estimates
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
                print('Residual kurtosis too high for', result[0])
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
            # just some extra cleanup
            se.replace('\"','')
            se = "".join(se.split())
            result.append(se.rstrip())
        if line.find('Individuals:') >= 0:
            n = line.split('duals:')[-1]
            result.append(n)
    fid.close()
    results.append(result)

fout = open(out_fname, 'w')
wr = csv.writer(fout)
wr.writerows(results)
fout.close()
