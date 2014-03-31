import mne
import numpy as np
import matplotlib.pyplot as plt


bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 50]]
subjs_fname = '/Users/sudregp/data/meg/aligned_subjs.txt'
data_dir = '/mnt/neuro/MEG_data/'
dir_out = '/users/sudregp/data/meg/'
fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]

x = range(len(subjs))
plt.figure(figsize=(10.2, 8.5))
bad_subjs = []
plt_cnt = 1
# grab data for all subjects
for l_freq, h_freq in bands:
    print 'Loading all subjects; band %d to %d Hz'%(l_freq, h_freq)
    mean_power = []
    for subj in subjs:
        fname = dir_out + 'lcmv-%dto%d-'%(l_freq,h_freq) + subj
        stc = mne.read_source_estimate(fname)
        mean_power.append(np.mean(stc.data))
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
plt.show()

bad_subjs = set([i for j in bad_subjs for i in j])
print 'Total bad = %d:'%len(bad_subjs), bad_subjs
print 'Remaining %d subjects.'%(len(subjs)-len(bad_subjs))
