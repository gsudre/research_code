import mne
import numpy as np


bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_pm2std.txt'
data_dir = '/Users/sudregp/data/meg_diagNoise_noiseRegp03_dataRegp001/'

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
dir_out = data_dir + '/connectivity/'
for cnt, s in enumerate(subjs[100:]):
    print cnt+1, '/', len(subjs), ':', s
    labels, label_colors = mne.labels_from_parc(s, parc='aparc')
    fwd_fname = '/mnt/neuro/MEG_data/analysis/rest/%s_rest_LP100_CP3_DS300_raw-5-fwd.fif'%s
    forward = mne.read_forward_solution(fwd_fname, surf_ori=True)
    for l_freq, h_freq in bands:
        print 'Band %d to %d Hz'%(l_freq, h_freq)
        fname = data_dir + 'lcmv-%dto%d-'%(l_freq,h_freq) + s
        stc = mne.read_source_estimate(fname)
        label_data = stc.extract_label_time_course(labels=labels,src=forward['src'],mode='pca_flip',allow_empty=True)
        # label_data is nlabels by time, so here we can use whatever connectivity method we fancy
        conn = np.corrcoef(label_data)
        np.save(dir_out + 'labelPCACorrelation-%dto%d-'%(l_freq,h_freq) + s, conn)

