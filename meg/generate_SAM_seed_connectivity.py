# Script to generate voxel time series
# by Gustavo Sudre, July 2014
import numpy as np
import mne
import os, sys
home = os.path.expanduser('~')
lib_path = os.path.abspath(home+'/research_code/meg/')
sys.path.append(lib_path)
import find_good_segments as fg


variant='' #'','_Z','_n','_nZ'
window_length=13.65  #s
fifs_dir = '/mnt/neuro/MEG_data/fifs/rest/'
out_dir = home + '/data/meg/sam%s'%variant + '/seed/'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
markers_fname = home+'/data/meg/marker_data_clean.npy'
markers = np.load(markers_fname)[()]       

# NOTE: These are not exactly the same coordinates as the ones in Evernote and in the papers because the ones there are in LPI system. Here, because we read in the files in AFNI standard, we need to flip the sign in the X and Y axis to make it RAI (see help page on whereami)
seed = [1, -44, 3]
seed_name = 'mPFC'
# seed = [ -14, 55, 25]
# seed_name = 'pCC'
# seed = [-8, -1, 38]
# seed_name = 'dACC'
# seed = [-46, -16, 5]
# seed_name = 'rIFG'
# seed = [-32, -40, 27]
# seed_name = 'rMFG' 

# find the source closest to the seed
coord = np.genfromtxt(home + '/sam/targetsInTLR.txt', delimiter=' ', skip_header=1)
dist = np.sqrt((coord[:,0] - seed[0])**2 + (coord[:,1] - seed[1])**2 + (coord[:,2] - seed[2])**2)
seed_src = np.argmin(dist)
print 'Seed src: %d, Distance to seed: %.2fmm'%(seed_src, np.min(dist))

# For each subject, we use the weight matrix to compute virtual electrodes
for s in subjs[:1]:
    weights = np.load(home + '/sam%s/'%variant + s + '_weights.npz')['weights']
    nsources = weights.shape[0]
    # normalize each beamformer weight by its vector norm
    normed = np.linalg.norm(weights, axis=1)
    weights = np.divide(weights.T,normed).T
    raw_fname = fifs_dir + '/%s_rest_LP100_CP3_DS300_raw.fif'%s
    raw = mne.fiff.Raw(raw_fname, preload=True, compensation=3)
    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    raw.filter(l_freq=1,h_freq=58,picks=picks)
    data, time = raw[picks, :]
    events = fg.get_good_events(markers[s], time, window_length)
    epochs = mne.Epochs(raw, events, None, 0, window_length, preload=True, baseline=None, detrend=0, picks=picks)
    sols = [np.dot(weights, epoch) for epoch in epochs]

    # we'll compute the connectivity from the seed to all other sources
    indices = mne.connectivity.seed_target_indices(seed_src,np.arange(nsources))

    con, freqs, times, n_epochs, n_tapers = mne.connectivity.spectral_connectivity(sols, indices=indices, method='wpli2_debiased', mode='multitaper', sfreq=raw.info['sfreq'], fmin=[1,4,8,13,30], fmax=[4,8,13,30,50], faverage=True, n_jobs=1, mt_adaptive=False)
    np.save(out_dir + s + '_' + seed_name + '_connectivity', con)