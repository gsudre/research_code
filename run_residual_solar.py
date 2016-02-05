# Runs the residuals from SOLAR through regressions with symptoms. Generates a table of heritability and pvalue, along with the r and p-value for inattention and HI, for each trait.
import os
import numpy as np
home = os.path.expanduser('~')
from scipy import stats
import csv
import glob


dir_name = home+'/data/solar/'
analysis = 'slimyeoipsi'
out_fname = dir_name + 'results_%s.csv'%analysis

folders = glob.glob(dir_name + analysis + '/*')

# gather all the traits we used
bivar_code = ['ae','an','inatt','hi','tinatt','thi']
traits = []
for folder in folders:
    res_dir = folder.split('/')[-1]
    # the trait name is represented by all directories that do not start with one of the bivariate analysis names
    if res_dir.split('_')[0] not in bivar_code:
        traits.append(res_dir)

# open the clinical data
sx_fname = dir_name + 'sx.csv'
sx = np.recfromcsv(sx_fname)

# for each SOLAR analysis
results = [['phen','h2r','h_pval','inatt','i_pval','hi','h_pval',
            't_now','p_now','t_ever','p_ever','anova','anova_p']]
for trait in traits:
    result = [trait]
    folder = dir_name + analysis + '/' + trait
    # grab the heritability estimates
    fname = folder+'/polygenic.out'
    fid = open(fname,'r')
    ignore_result = False
    for line in fid:
        if line.find('H2r is')>0:
            h2r = line.split('is ')[-1].split(' ')[0]
            p = line.split('= ')[-1].split(' ')[0]
            result.append(h2r)
            result.append(p)
        if line.find('No covariates')>=0:
            print 'No covariates used for', result[0]
            ignore_result = True
        if line.find('too high')>=0:
            print 'Residual kurtosis too high for', result[0]
    fid.close()

    if ignore_result:
        result = result + ['','','','','','','','','']
    else:
        # grab the residuals
        fname = folder+'/polygenic.residuals'
        residuals = np.recfromcsv(fname)
        # construct the residual and sx vector matching subjects
        x, inatt, hi = [], [], []
        g1_now, g1_ever = [], []
        g2_now, g2_ever = [], []
        g1, g2, g3 = [],[],[]
        for res in residuals:
            found = [rec for rec in sx if rec['mrn']==res['id']]
            if len(found)>0:
                # structures for correlation
                x.append(res['residual'])
                inatt.append(found[0]['inatt'])
                hi.append(found[0]['hi'])

                # ttest ever
                if found[0]['dx_ever']=='ADHD':
                    g1_ever.append(res['residual'])
                else:
                    g2_ever.append(res['residual'])
                # ttest now
                if found[0]['dx_now']=='ADHD':
                    g1_now.append(res['residual'])
                else:
                    g2_now.append(res['residual'])
                # anova
                if found[0]['sx_now']=='NV':
                    g1.append(res['residual'])
                elif found[0]['sx_now']=='persistent':
                    g2.append(res['residual'])
                else:
                    g3.append(res['residual'])

        r, p = stats.pearsonr(x, inatt)
        result.append(r)
        result.append(p)
        r, p = stats.pearsonr(x, hi)
        result.append(r)
        result.append(p)
        r, p = stats.ttest_ind(g1_now, g2_now)
        result.append(r)
        result.append(p)
        r, p = stats.ttest_ind(g1_ever, g2_ever)
        result.append(r)
        result.append(p)
        r, p = stats.f_oneway(g1, g2, g3)
        result.append(r)
        result.append(p)

    results.append(result)

fout = open(out_fname, 'w')
wr = csv.writer(fout)
wr.writerows(results)
fout.close()

