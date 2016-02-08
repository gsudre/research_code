# Grabs the significant variables from a SOLAR screening and formats it into a R formula
import os
home = os.path.expanduser('~')
import sys


trait = sys.argv[1]
analysis = 'dti_mean_3sd_extendedAndNuclear_combMvmtClean_mvmt12_bivar'
polygen = home + '/data/solar_paper_v2/%s/%s/polygenic.out' % (analysis, trait)

fid = open(polygen)
covariates = [l.split(' p =')[0] for l in fid if l.find('(Significant') > 0]
fid.close()

fmt_covariates = []
for c in covariates:
    # heritability doesn't count
    if c.find('H2r') < 0:
        # figuring out the single covariates
        fmt_sc = []
        sc = c.replace(' ', '').split('*')
        for i in sc:
            if i.find('^2') > 0:
                fmt_sc.append('I(%s)' % i)
            else:
                fmt_sc.append(i)
        fmt_covariates.append(':'.join(fmt_sc))
print ' + '.join(fmt_covariates)
