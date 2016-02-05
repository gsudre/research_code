# Script to generate voxel time series
# by Gustavo Sudre, July 2014
import numpy as np
import mne
import os, sys
home = os.path.expanduser('~')
lib_path = os.path.abspath(home+'/research_code/meg/')
sys.path.append(lib_path)
import find_good_segments as fg
import dsp_utils as dsp


variant='_nZ' #'','_Z','_n','_nZ'
bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
window_length=13.65  #s
fifs_dir = '/mnt/neuro/MEG_data/fifs/rest/'
out_dir = home + '/data/meg/sam%s'%variant + '/'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
markers_fname = home+'/data/meg/marker_data_clean.npy'
markers = np.load(markers_fname)[()]        

res = np.load(home+'/sam/rois.npz')
rois = list(res['rois'])
roi_voxels = list(res['roi_voxels'])

# For each subject, we use the weight matrix to compute virtual electrodes
for s in subjs:
    weights = np.load(home + '/sam%s/'%variant + s + '_weights.npz')['weights']
    # normalize each beamformer weight by its vector norm
    normed = np.linalg.norm(weights, axis=1)
    weights = np.divide(weights.T,normed).T
    raw_fname = fifs_dir + '/%s_rest_LP100_CP3_DS300_raw.fif'%s
    raw = mne.fiff.Raw(raw_fname, preload=True, compensation=3)
    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    data, time = raw[picks, :]
    events = fg.get_good_events(markers[s], time, window_length)
    epochs = mne.Epochs(raw, events, None, 0, window_length, preload=True, baseline=None, detrend=0, picks=picks)
    sols = [np.dot(weights, epoch) for epoch in epochs]

    # average the power across epochs. Here we need to average instead of adding up because otherwise subjects with higher number of epochs would always have higher power
    psd = 0
    for sol in sols:
        psd, freqs = dsp.compute_psd(sol, raw.info['sfreq'])
        psd += psd
    psd /= len(epochs)
    # Convert PSDs to dB
    psd = 10 * np.log10(psd)
    band_pow = []
    for band in bands:
        index = np.logical_and(freqs >= band[0], freqs <= band[1])
        vox_in_band_psd = np.mean(psd[:, index], axis=1)
        # average the power within rois
        roi_pow = [np.mean(vox_in_band_psd[np.array(vox)]) for vox in roi_voxels]
        band_pow.append(roi_pow)
    np.save(out_dir + s + '_roi_power', band_pow)