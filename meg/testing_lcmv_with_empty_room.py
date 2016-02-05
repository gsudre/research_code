import mne
import numpy as np

# subjs = ['MJKDJCWN', 'AKMNQNHX', 'CVKRVURL', 'EADHVJIM', 'ZSQTKJSC', 'APYSWYFP']
data_reg = .001
noise_reg = .03
# data_dir = '/home/sudregp/data/meg/' 
data_dir = '/mnt/neuro/MEG_data/'
dir_out = data_dir + 'meg_diagNoise_noiseRegp03_dataRegp001/' #'/Users/sudregp/data/meg_diagNoise_noiseRegp03_dataRegp001/'
empty_room_dir = '/Users/sudregp/data/meg_empty_room/' #data_dir + '/meg_empty_room/' #
bands = [[1, 4]]#, [4, 8], [8, 13], [13, 30], [30, 50]]
res = np.recfromtxt(empty_room_dir + 'closest_empty_room_data.csv',skip_header=0,delimiter=',')
closest_empty_room = {}
subjs = []
for rec in res:
    closest_empty_room[rec[0]] = str(rec[2])
    subjs.append(rec[0])
subjs=['JNTVOWPW']#['BXXVEOBE', 'MJWVOIGF', 'MNIYUFAG', 'WBTGYIHQ']

for subj in subjs:
    er_fname = empty_room_dir+'empty_room_'+closest_empty_room[subj]+'.fif'
    raw_fname = data_dir + 'fifs/rest/%s_rest_LP100_CP3_DS300_raw.fif'%subj
    fwd_fname = data_dir + 'analysis/rest/%s_rest_LP100_CP3_DS300_raw-5-fwd.fif'%subj
    forward = mne.read_forward_solution(fwd_fname, surf_ori=True)
    # we need to always reload raw because we bandpass and resample it, but copying it saves time
    raw_orig = mne.fiff.Raw(raw_fname, preload=True)
    er_raw_orig = mne.fiff.Raw(er_fname, preload=True, compensation=3)
    for l_freq, h_freq in bands:
        raw = raw_orig.copy()
        er_raw = er_raw_orig.copy()
        picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
        raw.filter(l_freq, h_freq, picks=picks)
        er_raw.filter(l_freq, h_freq, picks=picks)
        data_cov = mne.compute_raw_data_covariance(raw)
        noise_cov = mne.compute_raw_data_covariance(er_raw)
        # note that MNE reads CTF data as magnetometers!
        noise_cov = mne.cov.regularize(noise_cov, raw.info, mag=noise_reg)
        raw.apply_hilbert(picks, envelope=False)
        raw.resample(sfreq=1, stim_picks=picks)
        stc = mne.beamformer.lcmv_raw(raw, forward, noise_cov.as_diag(), data_cov, reg=data_reg, pick_ori=None, picks=picks)
        # stc.save(dir_out + 'lcmv-%dto%d-'%(l_freq,h_freq) + subj)

# # morph all subjects
# subject_to = 'fsaverage'
# for l_freq, h_freq in bands:
#     for subj in subjs:
#         fname = dir_out + 'lcmv-%dto%d-'%(l_freq,h_freq) + subj
#         stc_from = mne.read_source_estimate(fname)
#         vertices_to = [np.arange(10242), np.arange(10242)]
#         stc = mne.morph_data(subj, subject_to, stc_from, grade=vertices_to)
#         stc.save(dir_out + 'morphed-lcmv-%dto%d-'%(l_freq,h_freq) + subj)