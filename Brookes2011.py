import mne
import numpy as np
import virtual_electrode as ve

l_freq, h_freq = 13, 30
reg = 4
subjs_fname = '/Users/sudregp/data/meg/subjs.txt'
dir_out = '/users/sudregp/data/meg/'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

# # generating source space frequency envelopes
# for subj in subjs:
#     raw_fname = '/mnt/neuro/MEG_data/fifs/%s_rest_LP100_CP3_DS300_raw.fif'%subj
#     fwd_fname = '/mnt/neuro/MEG_data/analysis/rest/%s_rest_LP100_CP3_DS300_raw-5-fwd.fif'%subj

#     forward = mne.read_forward_solution(fwd_fname, surf_ori=True)
#     raw = mne.fiff.Raw(raw_fname, preload=True)
#     picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
#     raw.filter(l_freq, h_freq, picks=picks)
#     data_cov = mne.compute_raw_data_covariance(raw, picks=picks)
#     weights = ve.calculate_weights(forward, data_cov, reg=reg)
#     # downsample to 1 Hz effective sampling resolution. Note that the paper did this after beamforming, but we are safe to do it here as long as we get the covariance matrices before that. It'll make it go faster this way
#     raw.resample(1)
#     # instead of getting the hilbert of the source space (costly), do the Hilbert first and compute the envelope later
#     raw.apply_hilbert(picks, envelope=False)
#     data, times = raw[picks,:]
#     print 'Multiplying data by beamformer weights...'
#     # get the abs() of Hilbert transform (Hilbert envelope)
#     sol = abs(np.dot(weights, data))
#     stc = mne.SourceEstimate(sol, [forward['src'][0]['vertno'], forward['src'][1]['vertno']], times[0], times[1]-times[0])
#     stc.save('/Users/sudregp/data/meg/lcmv-beta-' + subj)

# morph and concatenate all subjects
init_sources = 25000
init_time = 24100
# create huge array so we can add all the data and thenresize it appropriately
data = np.empty([init_sources, init_time])
data[:] = np.nan
cnt = 0
subject_to = 'fsaverage'
for subj in subjs:
    fname = '/Users/sudregp/data/meg/lcmv-beta-' + subj
    stc_from = mne.read_source_estimate(fname)
    vertices_to = [np.arange(10242), np.arange(10242)]
    stc = mne.morph_data(subj, subject_to, stc_from, grade=vertices_to)
    data[0:stc.data.shape[0], cnt:(cnt+stc.data.shape[1])] = stc.data
    cnt += stc.data.shape[1]
print 'Resizing matrix'
data = data[:stc.data.shape[0], :cnt]
