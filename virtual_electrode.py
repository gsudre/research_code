import numpy as np
import dsp_utils as dsp


# import multiprocessing
# job_num = int(multiprocessing.cpu_count()/2)


def calculate_weights(forward, cov, reg=0, norm_weights=True):
# Make sure cov only has MEG data in it!

    inv_Cb = np.linalg.pinv(cov.data + reg * np.eye(cov.data.shape[0]))
    L = forward['sol']['data']
    nvectors = L.shape[1]
    # If we have more than one orientation per source, find the optimum
    # orientation following Sekihara et al. Asymptotic SNR of scalar and vector
    # minimum-variance beamformers for neuromagnetic source reconstruction. IEEE
    # Trans. Biomed. Eng, No 10, Vol. 51, 2004, pp 1726-1734. The code is also
    # somewhat borrowed from the Fieldtrip implementation.
    if forward['nsource'] < nvectors:
        optimal_orientation = np.zeros([3, forward['nsource']])
        for dip in range(forward['nsource']):
            # Separate the lead field for 3 orthogonal components
            ori = L[:306, (3 * dip):(3 * dip + 3)]
            U, S, V = np.linalg.svd(np.linalg.pinv(np.dot(ori.T, np.dot(inv_Cb, ori))))

            # The optimum orientation is the eigenvector that corresponds to the
            # MAXIMUM eigenvalue. However, we need to double check that this is
            # the case, because for single sphere head model, one of the
            # eigenvectors corresponds to the radial direction, giving lead fields
            # that are zero (to within machine precission). The eigenvalue
            # corresponding to this eigenvector can actually be the smallest and
            # can give the optimum (but wrong) Z-value!)

            ori1 = U[:, 1] / np.linalg.norm(U[:, 1])
            ori2 = U[:, 2] / np.linalg.norm(U[:, 2])

            # We only need to compare the eigenvectors that correspond to the two
            # biggest eigen values!

            L1 = np.dot(ori, ori1)
            L2 = np.dot(ori, ori2)

            if np.linalg.norm(L1) / np.linalg.norm(L2) < 1e-6:
            # the first orientation seems to be the silent orientation use the
            # second orientation instead
                optimal_orientation[:, dip] = ori2
            else:
                optimal_orientation[:, dip] = ori1
    else:
        optimal_orientation = forward['source_rr']

    weights = np.zeros([forward['nsource'], forward['nchan']])
    for dip in range(forward['nsource']):
        gain = L[:forward['nchan'], dip]
        num = np.dot(gain.T, inv_Cb)
        den = np.dot(num, gain)  # this is a scalar
        weights[dip, :] = num / den

    if norm_weights:
        normed_weights = np.sum(weights ** 2, axis=-1) ** (1. / 2)
        weights = weights / normed_weights[:, np.newaxis]

    return weights


def find_best_voxels(stc, rois, bands, job_num=1):
    # Returns the indices of the voxels with maximum power per band in each ROI, in the format roi x band. stc is SourceEstimate, rois is a list of Labels, and bands is a list of length 2 vectors

    fs = 1. / stc.tstep

    best_voxels = np.zeros([len(rois), len(bands)])
    for idr, roi in enumerate(rois):
        roi_activity = stc.in_label(roi)
        psds, freqs = dsp.compute_psd(roi_activity.data, fs, n_jobs=job_num)
        for idb, band in enumerate(bands):
            index = np.logical_and(freqs >= band[0], freqs <= band[1])
            band_psd = np.mean(psds[:, index], axis=1)
            best_voxels[idr, idb] = band_psd.argmax()
    return best_voxels


def compute_all_labels_pli(subj, tmax=np.Inf, reg=0, selected_voxels=None, rand_phase=False, job_num=1):

    import find_good_segments as fgs
    import mne
    import os
    import glob

    # Load real data as templates
    start, end, num_chans = fgs.find_good_segments(subj, threshold=3500e-15)

    if start == 0:
        start = start + 3

    if end - start > tmax:
        start = end - tmax

    bands = ([.5, 4], [4, 8], [8, 13], [13, 30], [30, 58])
    data_path = '/Users/sudregp/MEG_data/fifs/'
    fwd_path = '/Users/sudregp/MEG_data/analysis/rest/'

    raw = mne.fiff.Raw(data_path + subj + '_rest_LP100_HP0.6_CP3_DS300_raw.fif', preload=True)  # preloading makes computing the covariance a lot faster
    fwd_fname = fwd_path + subj + '_rest_LP100_HP0.6_CP3_DS300_raw-5-fwd.fif'

    # we don't need to choose picks because we only work with MEG channels, and
    # all channels are good
    fwd = mne.read_forward_solution(fwd_fname)

    labels_folder = os.environ['SUBJECTS_DIR'] + '/' + subj + '/labels/'
    label_names = glob.glob(labels_folder + '/*.label')

    print 'Reading subject labels...'
    labels = [mne.read_label(ln) for ln in label_names]

    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    cov = mne.compute_raw_data_covariance(raw, tmin=start, tmax=end, picks=picks)
    weights = calculate_weights(fwd, cov, reg=reg)

    data, times = raw[picks, raw.time_as_index(start):raw.time_as_index(end)]
    print 'Multiplying data by beamformer weights...'
    sol = np.dot(weights, data)
    src = mne.SourceEstimate(sol, (fwd['src'][0]['vertno'], fwd['src'][1]['vertno']), times[0], times[1] - times[0])

    # we can either figure out what vertices to use based on the overall power in each band, or just use pre-selected ones
    if selected_voxels is not None:
        print 'WARNING: using pre-selected vertices!'
    else:
        selected_voxels = find_best_voxels(src, labels, bands)

    # here we pick 5 artifact-free trials with 4096 samples (about 13s in the original paper) and use that as trials
    num_trials = 5
    num_samples = 4096
    label_activity = np.zeros([num_trials, len(labels), num_samples])
    pli = []

    # The voxels selected in each label change based on the band so we have to put the bands loop outside, instead of sending the same signal to spectral_connectivity and passing in several bands
    for band in np.arange(len(bands)):
        label_ts = np.zeros((len(labels), src.data.shape[1]))
        for idl, label in enumerate(labels):
            label_signal = src.in_label(label)
            label_ts = label_signal.data[selected_voxels[idl, band], :]

            # if we're randomizing the phase (whilst preserving power), then we offset the ROI time series by some random value
            if rand_phase:
                offset = np.random.randint(0, len(label_ts))
                label_ts = np.roll(label_ts, offset)

            cur = 0
            for trial in np.arange(num_trials):
                label_activity[trial, idl, :] = label_ts[cur:cur + num_samples]
                cur = cur + num_samples

        con = mne.connectivity.spectral_connectivity(label_activity,
            method='pli', mode='multitaper', sfreq=raw.info['sfreq'], fmin=bands[band][0], fmax=bands[band][1], faverage=True, mt_adaptive=True, n_jobs=job_num)[0]
        pli.append(np.squeeze(con))

    return pli, labels, bands, selected_voxels
