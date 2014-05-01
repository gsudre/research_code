import mne
import numpy as np
from virtual_electrode import calculate_weights
from scipy import stats
from sklearn.decomposition import FastICA

bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
reg = 4
subjs_fname = '/Users/sudregp/data/meg/usable_subjects_pm2std.txt'
data_dir = '/mnt/neuro/MEG_data/'
dir_out = '/Users/sudregp/data/meg/'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()

# # generating source space frequency envelopes
# for subj in subjs:
#     raw_fname = data_dir + 'fifs/%s_rest_LP100_CP3_DS300_raw.fif'%subj
#     fwd_fname = data_dir + 'analysis/rest/%s_rest_LP100_CP3_DS300_raw-5-fwd.fif'%subj
#     forward = mne.read_forward_solution(fwd_fname, surf_ori=True)
#     for l_freq, h_freq in bands:
#         # we need to always reload raw because we bandpass and resample it
#         raw = mne.fiff.Raw(raw_fname, preload=True)
#         picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
#         raw.filter(l_freq, h_freq, picks=picks)
#         data_cov = mne.compute_raw_data_covariance(raw, picks=picks)
#         weights = calculate_weights(forward, data_cov.data, reg=reg)
#         # downsample to 1 Hz effective sampling resolution. Note that the paper did this after beamforming, but we are safe to do it here as long as we get the covariance matrices before that. It'll make it go faster this way
#         raw.resample(1)
#         # instead of getting the hilbert of the source space (costly), do the Hilbert first and compute the envelope later
#         raw.apply_hilbert(picks, envelope=False)
#         data, times = raw[picks,:]
#         print 'Multiplying data by beamformer weights...'
#         # get the abs() of Hilbert transform (Hilbert envelope)
#         sol = abs(np.dot(weights, data))
#         stc = mne.SourceEstimate(sol, [forward['src'][0]['vertno'], forward['src'][1]['vertno']], times[0], times[1]-times[0], subject=subj)
#         stc.save(dir_out + 'lcmv-%dto%d-'%(l_freq,h_freq) + subj)

# # morph all subjects
# subject_to = 'fsaverage'
# for subj in subjs:
#     fname = '/Users/sudregp/data/meg/lcmv-beta-' + subj
#     stc_from = mne.read_source_estimate(fname)
#     vertices_to = [np.arange(10242), np.arange(10242)]
#     stc = mne.morph_data(subj, subject_to, stc_from, grade=vertices_to)
#     stc.save('/Users/sudregp/data/meg/morphed-lcmv-beta-' + subj)


# concatenate all subjects and apply ICA
band_ICs = []
band_corr_ICs = []
for l_freq, h_freq in bands:
    print 'Concatenating sources in band %d to %d Hz'%(l_freq, h_freq)
    init_sources = 20500
    init_time = 38500
    # create huge array so we can add all the data and then resize it appropriately
    data = np.empty([init_sources, init_time])
    data[:] = np.nan
    cnt = 0
    for subj in subjs:
        fname = dir_out + 'morphed-lcmv-%dto%d-'%(l_freq,h_freq) + subj
        stc= mne.read_source_estimate(fname)
        # mean correcting and normalizing variance
        data[0:stc.data.shape[0], cnt:(cnt+stc.data.shape[1])] = \
            stats.mstats.zscore(stc.data, axis=1)
        cnt += stc.data.shape[1]
    data = data[:stc.data.shape[0], :cnt]

    # applying ICA and figuring out how each IC scores
    print 'Applying FastICA'
    ica = FastICA(n_components=30, random_state=0)
    ICs = ica.fit_transform(data.T).T
    corr_ICs = []
    for i in range(ICs.shape[0]):
        print 'Scoring IC', i+1, '/', ICs.shape[0]
        corrs = np.empty([data.shape[0],1])
        corrs[:] = np.nan
        for s in range(data.shape[0]):
            r, p = stats.pearsonr(ICs[i,:], data[s,:])
            corrs[s] = r
        corr_ICs.append(corrs)

    band_ICs.append(ICs)
    band_corr_ICs.append(corr_ICs)
