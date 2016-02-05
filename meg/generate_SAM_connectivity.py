# Script to calculate connectivity in SAM time series per ROI
# by Gustavo Sudre, July 2014
import numpy as np
import mne
import os
home = os.path.expanduser('~')


bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
method=['pli','imcoh','plv','wpli','pli2_unbiased','wpli2_debiased']
window_length=13.65  #s
fifs_dir = '/mnt/neuro/MEG_data/fifs/rest/'
data_dir = home + '/data/meg/sam_Z_noNorm/'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
markers_fname = home+'/data/meg/marker_data_clean.npy'
markers = np.load(markers_fname)[()]

# For each subject, we use the weight matrix to compute virtual electrodes
for s in subjs:
    data = np.load(data_dir + s + '_roi_data.npz')['data']
    conn = []
    for idx, band in enumerate(bands):
        print '\n\nsubject %s, band %d\n\n'%(s,idx)
        subj_conn = mne.connectivity.spectral_connectivity(data[idx], method=method, mode='multitaper', sfreq=300, fmin=band[0], fmax=band[1], faverage=True, n_jobs=1, mt_adaptive=False)[0]
        conn.append(subj_conn)
    np.save(data_dir + s + '_roi_connectivity', np.array(conn))
