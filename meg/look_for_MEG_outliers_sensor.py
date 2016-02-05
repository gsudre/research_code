import mne
import numpy as np
import matplotlib.pyplot as plt


bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
subjs_fname = '/Users/sudregp/data/meg/good_subjects.txt'
data_dir = '/mnt/neuro/MEG_data/'
dir_out = '/users/sudregp/data/meg/'
fid = open(subjs_fname, 'r')
# subjs = [line.rstrip() for line in fid]

subjs = ['MJKDJCWN', 'AKMNQNHX', 'CVKRVURL', 'EADHVJIM', 'ZSQTKJSC', 'APYSWYFP']

# grab data for all subjects
all_power = []
for subj in subjs:
    subj_power = []
    print 'Loading subject %s'%(subj)
    raw_fname = data_dir + 'fifs/%s_rest_LP100_CP3_DS300_raw.fif'%subj
    raw = mne.fiff.Raw(raw_fname, preload=True)
    picks = mne.fiff.pick_channels_regexp(raw.info['ch_names'], 'M..-*')
    [psd, freqs] = mne.time_frequency.compute_raw_psd(raw=raw,picks=picks,plot=False,fmin=1,fmax=50,tmin=0,tmax=239)
    for l_freq, h_freq in bands:
        idx = np.logical_and(freqs>=l_freq, freqs<=h_freq)
        # psd = 10 * np.log10(psd)
        subj_power.append(np.mean(psd[:,idx]))
    all_power.append(subj_power)

x = range(len(all_power))
plt.figure(figsize=(10.2, 8.5))
bad_subjs = []
plt_cnt = 1
for fidx, (l_freq, h_freq) in enumerate(bands):
    mean_power = np.array([p[fidx] for p in all_power])
    plt.subplot(3,2,plt_cnt)
    plt.plot(x, mean_power, 'ko')
    my_mean = np.mean(mean_power)
    std_mean = np.std(mean_power)
    h_thresh = my_mean + 2*std_mean
    l_thresh = my_mean - 2*std_mean

    band_bad_subjs = [subjs[i] for i in range(len(subjs)) if mean_power[i]<l_thresh or mean_power[i]>h_thresh]
    print 'Bad in %d-%d Hz = %d: %s'%(l_freq, h_freq, len(band_bad_subjs), band_bad_subjs)
    bad_subjs.append(band_bad_subjs)

    # plotting
    plt.plot(x,my_mean*np.ones(len(x)),'r-',linewidth=2)
    plt.plot(x,h_thresh*np.ones(len(x)),'r--',linewidth=2)
    plt.plot(x,l_thresh*np.ones(len(x)),'r--',linewidth=2)
    plt.title('%s to %s Hz'%(l_freq, h_freq))
    plt_cnt += 1
plt.xlabel('Subject')
plt.ylabel('Mean power')
plt.show(block=False)

bad_subjs = set([i for j in bad_subjs for i in j])
print 'Total bad = %d:'%len(bad_subjs), bad_subjs
print 'Remaining %d subjects.'%(len(subjs)-len(bad_subjs))


# for i in reversed(a):
#     idx = subjs.index(i)
#     print idx
#     del all_power[idx]
#     del subjs[idx]