import sys
import os
home = os.path.expanduser('~')
import numpy as np
from sklearn.decomposition import FastICA

if len(sys.argv) > 1:
    subj = sys.argv[1]
else:
    subj = 'subj1'

nreals = 40
ncomps = 30
rng = np.random.RandomState()
res_dir = home + '/data/results/graicar/fmri/'

execfile(home + '/research_code/graicar/load_fMRI_data.py')

for i in range(nreals):
    print 'Realization %d of %d' % (i+1, nreals)
    ica = FastICA(n_components=ncomps, random_state=rng)
    # return the first dimension as the number of ICs
    ICs = ica.fit_transform(data).T
    np.savez(res_dir + subj + '_R%02d' % i, ICs=ICs)
