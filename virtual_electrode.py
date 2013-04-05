import numpy as np
import dsp_utils as dsp
import mne
import env
import pdb


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
        power = np.dot(gain.T, inv_Cb)
        den = np.dot(power, gain)  # this is a scalar
        weights[dip, :] = power / den

    if norm_weights:
        normed_weights = np.sum(weights ** 2, axis=-1) ** (1. / 2)
        weights = weights / normed_weights[:, np.newaxis]

    return weights, power


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


def find_best_voxels_epochs(stcs, rois, bands, job_num=1, verbose=True):
    # Returns the indices of the voxels with maximum power per band in each ROI, in the format roi x band. stc is SourceEstimate, rois is a list of Labels, and bands is a list of length 2 vectors

    fs = 1. / (stcs[0].times[1] - stcs[0].times[0])

    best_voxels = np.zeros([len(rois), len(bands)])
    for idr, roi in enumerate(rois):
        if verbose:
            print '\nLooking for best voxel in label ' + str(idr+1) + '/' + str(len(rois))
        # in each label, we sum the power over all epochs
        psd = 0
        bad_label = False
        for stc in stcs:
            try:
                roi_activity = stc.in_label(roi)
                tmp, freqs = dsp.compute_psd(roi_activity.data, fs, n_jobs=job_num)
                # psd is voxels x freqs
                psd += tmp
            except ValueError:
                print "Oops! No vertices in this label!"
                bad_label = True

        # then find the voxel with biggest power in each band. If there are no voxels in the label, replace it by NAN
        if bad_label:
            best_voxels[idr, :] = np.NaN
        else:
            for idb, band in enumerate(bands):
                index = np.logical_and(freqs >= band[0], freqs <= band[1])
                # taking care of the weird case in which there's only one voxel in the label
                freq_axis = len(psd.shape) - 1
                band_psd = np.mean(psd[:, index], axis=freq_axis)
                best_voxels[idr, idb] = band_psd.argmax()
    return best_voxels


def localize_activity(subj, tmax=np.Inf, clean_only=True, reg=0):
    import find_good_segments as fgs

    data_path = env.data + '/MEG_data/fifs/'
    fwd_path = env.data + '/MEG_data/analysis/rest/'
    fwd_fname = fwd_path + subj + '_rest_LP100_HP0.6_CP3_DS300_raw-5-fwd.fif'

    # preloading makes computing the covariance a lot faster
    raw = mne.fiff.Raw(data_path + subj + '_rest_LP100_HP0.6_CP3_DS300_raw.fif', preload=True)

    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')

    # we don't need to choose picks because we only work with MEG channels, and
    # all channels are good
    fwd = mne.read_forward_solution(fwd_fname)

    # Load real data as templates
    if clean_only:
        start, end, num_chans = fgs.find_good_segments(subj, threshold=3500e-15)
        if start == 0:
            start = start + 3

        if end - start > tmax:
            start = end - tmax

        cov = mne.compute_raw_data_covariance(raw, tmin=start, tmax=end, picks=picks)
    else:
        cov = mne.compute_raw_data_covariance(raw, picks=picks)

    weights = calculate_weights(fwd, cov, reg=reg)

    data, times = raw[picks, raw.time_as_index(start):raw.time_as_index(end)]
    print 'Multiplying data by beamformer weights...'
    sol = np.dot(weights, data)
    src = mne.SourceEstimate(sol, [fwd['src'][0]['vertno'], fwd['src'][1]['vertno']], times[0], times[1] - times[0])
    return src


def localize_epochs(epochs, fwd, reg=0):
    ''' Returns a list of Sourceestimates, one per Epoch '''

    cov = mne.compute_covariance(epochs)
    weights, _ = calculate_weights(fwd, cov, reg=reg)
    stcs = []
    print 'Multiplying data by beamformer weights...'
    for epoch in epochs:
        sol = np.dot(weights, epoch)
        src = mne.SourceEstimate(sol, [fwd['src'][0]['vertno'], fwd['src'][1]['vertno']], epochs.tmin, epochs.times[1] - epochs.times[0])
        stcs.append(src)

    return stcs


def compute_pli(src, labels, selected_voxels, bands, randomize=False, job_num=1):
    # here we pick 5 artifact-free trials with 4096 samples (about 13s in the original paper) and use that as trials
    num_trials = 5
    num_samples = 4096
    label_activity = np.zeros([num_trials, len(labels), num_samples])
    pli = []

    sfreq = 1. / (src.times[1] - src.times[0])

    # The voxels selected in each label change based on the band so we have to put the bands loop outside, instead of sending the same signal to spectral_connectivity and passing in several bands
    for band in np.arange(len(bands)):
        label_ts = np.zeros((len(labels), src.data.shape[1]))
        for idl, label in enumerate(labels):
            label_signal = src.in_label(label)
            label_ts = label_signal.data[selected_voxels[idl, band], :]

            # if we're randomizing the phase (whilst preserving power), then we offset the ROI time series by some random value
            if randomize:
                # we are randomizing the phase, so the shift should be within one complete cycle of the fastest frequency in the band
                cycle = 1. / bands[band][1] * sfreq
                offset = np.random.randint(0, cycle)
                label_ts = np.roll(label_ts, offset)

            cur = 0
            for trial in np.arange(num_trials):
                label_activity[trial, idl, :] = label_ts[cur:cur + num_samples]
                cur = cur + num_samples

        con = mne.connectivity.spectral_connectivity(label_activity, method='pli', mode='multitaper', sfreq=sfreq, fmin=bands[band][0], fmax=bands[band][1], faverage=True, mt_adaptive=True, n_jobs=job_num)[0]

        pli.append(np.squeeze(con))
    return pli


def compute_pli_epochs(stcs, labels, selected_voxels, bands, randomize=False, job_num=1):

    pli = []
    sfreq = 1. / (stcs[0].times[1] - stcs[0].times[0])
    label_activity = np.zeros([len(stcs), len(labels), len(stcs[0].times)])

    # The voxels selected in each label changes based on the band so we have to put the bands loop outside, instead of sending the same signal to spectral_connectivity and passing in several bands
    for band in np.arange(len(bands)):
        for idl, label in enumerate(labels):
            for s, stc in enumerate(stcs):
                voxel = selected_voxels[idl, band]
                # in the case where there were no voxels in the label, replace the label timecourse by nans
                if np.isnan(voxel):
                    label_ts = np.empty((1, len(stc.times)))
                    label_ts[:] = np.NAN
                else:
                    label_signal = stc.in_label(label)
                    label_ts = label_signal.data[voxel, :]

                # if we're randomizing the phase (whilst preserving power), then we offset the ROI time series by some random value
                if randomize:
                    # we are randomizing the phase, so the shift should be within one complete cycle of the fastest frequency in the band
                    cycle = 1. / bands[band][1] * sfreq
                    offset = np.random.randint(0, cycle)
                    label_ts = np.roll(label_ts, offset)

                label_activity[s, idl, :] = label_ts
        con = mne.connectivity.spectral_connectivity(label_activity, method='pli', mode='multitaper', sfreq=sfreq, fmin=bands[band][0], fmax=bands[band][1], faverage=True, mt_adaptive=True, n_jobs=job_num)[0]

        pli.append(np.squeeze(con))
    return pli


def compute_all_labels_pli(subj, selected_voxels=None, rand_phase=0, job_num=1, tmax=np.Inf, reg=0):

    import os
    import glob

    bands = ([.5, 4], [4, 8], [8, 13], [13, 30], [30, 58])

    labels_folder = os.environ['SUBJECTS_DIR'] + '/' + subj + '/labels/'
    label_names = glob.glob(labels_folder + '/*.label')

    print 'Reading subject labels...'
    labels = [mne.read_label(ln) for ln in label_names]

    src = localize_activity(subj, tmax=tmax, reg=reg)

    # we can either figure out what vertices to use based on the overall power in each band, or just use pre-selected ones
    if selected_voxels is not None:
        print 'WARNING: using pre-selected vertices!'
    else:
        selected_voxels = find_best_voxels(src, labels, bands, job_num)

    if rand_phase == 0:
        pli = compute_pli(src, labels, selected_voxels, bands, job_num=job_num)
    else:
        import time
        rand_plis = np.zeros([rand_phase, len(bands), len(labels), len(labels)])
        for r in range(rand_phase):
            print '==================================='
            print '========  Permutation ' + str(r+1) + ' ==========='
            print '==================================='
            pli = compute_pli(src, labels, selected_voxels, bands, job_num=job_num, randomize=True)
            for band in range(len(bands)):
                rand_plis[r, band, :, :] = pli[band]

        np.savez(env.results + 'rand_' + str(rand_phase) + '_plis_' + subj + '_' + str(int(time.time())), rand_plis=rand_plis)

    return pli, labels, bands, selected_voxels
