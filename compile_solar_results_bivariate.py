# Grabs the results from SOLAR univariate and bivariate analysis and formats it
# into a nice table.
import os
from math import *
import csv
import glob
home = os.path.expanduser('~')


dir_name = home + '/data/solar_paper_v2/'
analysis = 'dti_mean_3sd_extendedAndNuclear_combMvmtClean_full_bivar_extended'
out_fname = dir_name + 'polygen_bivar_results_%s.csv' % analysis

folders = glob.glob(dir_name + analysis + '/*')

# bivar = ['adhd_ever','adhd_now','inatt','hi','total','i_inatt','i_hi']
# bivar_code = ['ae','an','inatt','hi','total','tinatt','thi']
bivar = ['inatt', 'hi', 'total', 'i_inatt', 'i_hi', 'i_total', 'DX',
         'DX_inatt', 'DX_hi', 'DX_comb']
bivar_code = ['inatt', 'hi', 'total', 'tinatt', 'thi', 'ttotal', 'DX',
              'DXinatt', 'DXhi', 'DXcomb']

header = ['phen', 'h2r', 'h_pval', 'h2r_se', 'c2', 'c2_pval', 'high_kurtosis']
header += [i + j for i in bivar for j in ['_erv', '_pval', '_rhog', '_rhoe',
                                          '_rhop', '_h2e', '_h2i']]

results = [header]

# gather all the traits we used
traits = []
for folder in folders:
    res_dir = folder.split('/')[-1]
    # the trait name is represented by all directories that do not start with
    # one of the bivariate analysis names we also make sure the trait directory
    # has a valid polygen.out file
    if res_dir.split('_')[0] not in bivar_code:
        folder = dir_name + analysis + '/' + res_dir
        fname = folder + '/polygenic.out'
        good_trait = False
        fid = open(fname, 'r')
        for line in fid:
            if "H2r" in line:
                good_trait = True
        fid.close()
        if good_trait:
            traits.append(res_dir)

for trait in traits:
    result = [trait]
    # grab the univariate heritability estimates
    folder = dir_name + analysis + '/' + trait
    fname = folder + '/polygenic.out'
    fid = open(fname, 'r')
    c2 = -1
    se = -1
    for line in fid:
        if line.find('H2r is') >= 0:
            h2r = line.split('is ')[-1].split(' ')[0]
            p = line.split('= ')[-1].split(' ')[0]
            result.append(h2r)
            result.append(p)
            # there's no SE when h2r is 0
            if float(h2r) < 0.000000001:
                result.append(0)
                se = 0
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
            # if we got here but haven't seen any C2, then we didn't calculate
            # it. same thing for standard error
            if se == -1:
                result.append(0)
            if c2 == -1:
                result.append('')
                result.append('')
            if line.find('too high') > 0:
                print 'Residual kurtosis too high for', result[0]
                result.append(1)
            else:
                result.append(0)
        if line.find('H2r Std. Error:') >= 0:
            se = line.split(':')[-1]
            result.append(se)
    fid.close()

    # collect the results for each bivariate analysis
    for b_name, b_code in zip(bivar, bivar_code):
        folder = dir_name + analysis + '/' + b_code + '_' + trait
        fname = folder+'/polygenic.out'
        fid = open(fname, 'r')
        for line in fid:
            if line.find('H2r(%s) is' % b_name) >= 0:
                h2i = float(line.split('is ')[-1].split(' ')[0])
            if line.find('H2r(%s) is' % ('i_' + trait)) >= 0:
                h2e = float(line.split('is ')[-1].split(' ')[0])
            if line.find('RhoG is') >= 0:
                rhog = float(line.split('is ')[-1].split(' ')[0])
            if line.find('RhoG different from zero') >= 0:
                p = line.split('= ')[-1].split(' ')[0]
            if line.find('RhoE is') >= 0:
                rhoe = float(line.split('is ')[-1].split(' ')[0])
            if line.find('Derived Estimate of RhoP') >= 0:
                rhop = float(line.split('is ')[-1].split(' ')[0])
        fid.close()
        erv = abs(sqrt(h2i) * sqrt(h2e) * rhog)
        result += [erv, p, rhog, rhoe, rhop, h2e, h2i]
    results.append(result)

fout = open(out_fname, 'w')
wr = csv.writer(fout)
wr.writerows(results)
fout.close()
