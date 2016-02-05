import sys
import os
home = os.path.expanduser('~')
import numpy as np
from sklearn.decomposition import FastICA

if len(sys.argv) > 2:
    subj, freq_band = sys.argv[1:]
    res_dir = home + '/data/results/graicar/meg/'
    execfile(home + '/research_code/graicar/load_MEG_data.py')
elif len(sys.argv) > 1:
    subj = sys.argv[1]
    freq_band = None
    res_dir = home + '/data/results/graicar/fmri/'
    execfile(home + '/research_code/graicar/load_fMRI_data.py')
else:
    # subj = 'JOAOCEOG'
    # freq_band = '8-13'
    # res_dir = home + '/data/results/graicar/meg/'
    # execfile(home + '/research_code/graicar/load_MEG_data.py')
    subj = 'subj1'
    freq_band = None
    es_dir = home + '/data/results/graicar/fmri/'
    execfile(home + '/research_code/graicar/load_fMRI_data.py')

nreals = 60
ncomps = 30
rng = np.random.RandomState()

for i in range(nreals):
    print 'Realization %d of %d' % (i+1, nreals)
    ica = FastICA(n_components=ncomps, random_state=rng)
    # return the first dimension as the number of ICs
    ICs = ica.fit_transform(data).T
    if freq_band is not None:
        fname = res_dir + subj + '_' + freq_band + '_R%02d.npz' % i
    else:
        fname = res_dir + subj + '_R%02d.npz' % i
    np.savez(fname, ICs=ICs)
