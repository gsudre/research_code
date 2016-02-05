''' Tests whether the average connectivity of nodes within a network is higher than nodes not in the network '''

import mne
import numpy as np
from scipy import stats

hemi = 'rh'
seed = 'isthmuscingulate-rh'
in_network = ['superiorfrontal-rh', 'inferiorparietal-rh']
bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_pm2std_withFamily.txt'
data_dir = '/Users/sudregp/data/meg_diagNoise_noiseRegp03_dataRegp001/'
g1_fname = '/Users/sudregp/data/meg/nv_subjs.txt'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid1 = open(g1_fname, 'r')
g1 = [line.rstrip() for line in fid1]

in_conn = [[] for b in range(5)]
out_conn = [[] for b in range(5)]
for s in subjs:
    if s in g1:
        labels, label_colors = mne.labels_from_parc(s, parc='aparc')
        label_names = [l.name for l in labels]
        fname = data_dir + 'connectivity/pli-%s.npy'%(s)
        conn = np.load(fname)[()]
        seed_idx = label_names.index(seed)
        hemi_labels = [l for l in label_names if l.find('-'+hemi)>0]
        out_network = list(np.setdiff1d(set(hemi_labels), set(in_network + [seed])))
        for b in range(5):
            in_conn[b].append(np.mean([conn[seed_idx, label_names.index(i), b] for i in in_network]))
            out_conn[b].append(np.mean([conn[seed_idx, label_names.index(i), b] for i in out_network]))
for b in range(5):
    print stats.ttest_ind(in_conn[b],out_conn[b]), np.mean(in_conn[b]), np.mean(out_conn[b])


