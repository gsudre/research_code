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


variant='_Z' #'','_Z','_n','_nZ'
bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
window_length=13.65  #s
fifs_dir = '/mnt/neuro/MEG_data/fifs/rest/'
out_dir = home + '/data/meg/sam%s'%variant + '_noNorm/'
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
for s in subjs[62:]:
    weights = np.load(home + '/sam%s/'%variant + s + '_weights.npz')['weights']
    # normalize each beamformer weight by its vector norm
    # normed = np.linalg.norm(weights, axis=1)
    # weights = np.divide(weights.T,normed).T
    raw_fname = fifs_dir + '/%s_rest_LP100_CP3_DS300_raw.fif'%s
    raw = mne.fiff.Raw(raw_fname, preload=True, compensation=3)
    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    raw.filter(l_freq=1,h_freq=58,picks=picks)
    data, time = raw[picks, :]
    events = fg.get_good_events(markers[s], time, window_length)
    epochs = mne.Epochs(raw, events, None, 0, window_length, preload=True, baseline=None, detrend=0, picks=picks)
    sols = [np.dot(weights, epoch) for epoch in epochs]

    # in each ROI, choose the VE with highest power in that band
    psd = 0
    for sol in sols:
        psd, freqs = dsp.compute_psd(sol, raw.info['sfreq'])
        psd += psd
    band_signal = []
    for band in bands:
        index = np.logical_and(freqs >= band[0], freqs <= band[1])
        band_psd = np.mean(psd[:, index], axis=1)
        # generate a list of (n_signals, n_times) epochs, where each signal represents one ROI
        roi_series = []
        for vox in roi_voxels:
            roi_psd = band_psd[np.array(vox)]
            # the process of normalization introduces NaNs, so we need to be careful here. If all voxels in the ROI are NaN, return NaNs
            try:
                max_vox = np.array(vox)[np.nanargmax(roi_psd)]
            except:
                max_vox = vox[0]
            roi_series.append([sol[max_vox, :] for sol in sols])
        band_signal.append(roi_series)
    data = [np.array(signal).swapaxes(0,1) for signal in band_signal]
    np.savez(out_dir + s + '_roi_data', data=data, rois=rois, roi_voxels=roi_voxels, bands=bands)