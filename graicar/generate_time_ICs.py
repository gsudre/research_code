import sys
import os
home = os.path.expanduser('~')
import numpy as np
from sklearn.decomposition import FastICA
import glob


if len(sys.argv) > 1:
    subj, freq_band = sys.argv[1:]
else:
    subj = 'JOAOCEOG'
    freq_band = '8-13'

nreals = 60
ncomps = 30
rng = np.random.RandomState()
res_dir = home + '/data/results/graicar/meg/'

execfile(home + '/research_code/graicar/load_MEG_data.py')

# check how many iterations have completed
files = glob.glob(res_dir + subj + '_' + freq_band + '_R*.npz')
for i in range(len(files), nreals):
    print 'Realization %d of %d' % (i + 1, nreals)
    ica = FastICA(n_components=ncomps, random_state=rng)
    # return the first dimension as the number of ICs
    ICs = ica.fit_transform(data.T).T
    np.savez(res_dir + subj + '_' + freq_band + '_R%02d' % i, ICs=ICs)
