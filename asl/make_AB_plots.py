''' Script to parse the log from run_multiple_procPCASL.sh and make Bland-Altman plots'''
import re
import numpy as np
import matplotlib.pyplot as plt
import os
home = os.path.expanduser('~')

# maskids = ['1362','1378','1380','1388','1389','1395','1463','1464','1474','1475'] #vid
maskids = ['1362','1378','1380','1388','1389','1395','1474','1475'] #vid without people with more than 20cm mvmt
# maskids = ['1362','1378','1380','1388','1389','1395','1464'] #tfree
log_dir = home + '/data/results/asl/'
nvols = 23
task = 'vid'
plot_thresh = [.05, .3]
plot_rois = ['Putamen','Thalamus','Caudate','Superior_Temporal_Gyrus','Superior_Occipital_Gyrus']
# plot_rois = ['Medial_Globus_Pallidus','Putamen','Superior_Temporal_Gyrus','Thalamus','Medial_Frontal_Gyrus','Inferior_Parietal_Lobule','Lateral_Globus_Pallidus','Caudate','Superior_Occipital_Gyrus']
plot_rois = [hemi+roi for roi in plot_rois for hemi in ['left-','right-']]

# From http://stackoverflow.com/questions/16399279/bland-altman-plot-in-python
def bland_altman_plot(data1, data2, title_str, *args, **kwargs):
    data1     = np.asarray(data1)
    data2     = np.asarray(data2)
    mean      = np.mean([data1, data2], axis=0)
    diff      = data1 - data2                   # Difference between data1 and data2
    md        = np.mean(diff)                   # Mean of the difference
    sd        = np.std(diff, axis=0)            # Standard deviation of the difference

    plt.scatter(mean, diff, *args, **kwargs)
    plt.axhline(md,        color='gray', linestyle='--')
    plt.axhline(md + 2*sd, color='gray', linestyle='--')
    plt.axhline(md - 2*sd, color='gray', linestyle='--')
    plt.title(title_str)


# Because of how the log files are created, it's cheaper to read all logs first, organize them, and create the plots later
# data has two lists of dicts. lists are ordered the same ways as maskids, and dicts are keyed by ROIs. Each value in dict is a list with ROI values, ordered by thresh
data = []
for obs in range(2):
    obs_data = []
    for maskid in maskids:
        fname = log_dir + '/log_%s_%s%d.txt'%(maskid,task,obs+1) 
        thresh = []
        outliers = []
        label_data = {}
        fid = open(fname,'r')
        waiting_for_value = False
        label_name = 'no_label'
        for line in fid:
            if waiting_for_value:
                waiting_for_value = False
                obj = re.search('^(\S+)', line)
                cbf = float(obj.group(1))
                if label_name in label_data.keys():
                    label_data[label_name].append(cbf)
                else:
                    label_data[label_name] = [cbf]
            else:
                obj = re.search('^Outlier detection threshold = (.+)*', line)
                if obj is not None:
                    thresh.append(float(obj.group(1)))
                obj = re.search('^Num. outlier volumes = (\d+)*, Outlier', line)
                if obj is not None:
                    outliers.append(100*(1-float(obj.group(1))/nvols))
                obj = re.search('^::(\w+):(\w+)::', line)
                if obj is not None:
                    label_name = obj.group(1) + '-' + obj.group(2)
                    waiting_for_value = True
        obs_data.append(label_data)
    data.append(obs_data)

# Now work on some plots. We need one plot for each plotting threshold. Each plot has a subplot for individual ROIs
for t in plot_thresh:
    k = thresh.index(t)
    plt.figure(figsize=(10, 12))
    for r, roi in enumerate(plot_rois):
        plt.subplot(len(plot_rois)/2,2,r+1)
        data1 = [d[roi][k] for d in data[0]]
        data2 = [d[roi][k] for d in data[1]]
        bland_altman_plot(data1, data2, '%s (%s: %.2f)'%(roi,task,t))
        if r==(len(plot_rois)-2):
            plt.xlabel('mean(s1,s2)')
            plt.ylabel('diff(s1,s2)')
    plt.tight_layout()

# Plots for raw data, one plot per ROI
for t in plot_thresh:
    k = thresh.index(t)
    plt.figure(figsize=(10, 12))
    for r, roi in enumerate(plot_rois):
        plt.subplot(len(plot_rois)/2,2,r+1)
        data1 = [d[roi][k] for d in data[0]]
        data2 = [d[roi][k] for d in data[1]]
        y = np.vstack([data1, data2])
        x = [1,2]
        plt.plot(x,y,'.-',linewidth=2)
        plt.xlim([.8, 2.2])
        plt.title('%s (%s: %.2f)'%(roi,task,t))
        if r==(len(plot_rois)-2):
            plt.ylabel('CBF')
            plt.xlabel('Observation')
    plt.tight_layout()

# # Plots for total movement and difference correlation
# motion = []
# for maskid in maskids:
#     subj_motion = 0
#     for obs in range(2):
#         fname = home + '/data/asl/processed/%s/motion.%s%d.enorm.1D'%(maskid,task,obs+1)
#         enorm = np.genfromtxt(fname)
#         subj_motion += np.sum(enorm)
#     motion.append(subj_motion)
# from scipy import stats
# for t in plot_thresh:
#     k = thresh.index(t)
#     plt.figure(figsize=(10, 12))
#     for r, roi in enumerate(plot_rois):
#         plt.subplot(len(plot_rois)/2,2,r+1)
#         data1 = np.array([d[roi][k] for d in data[0]])
#         data2 = np.array([d[roi][k] for d in data[1]])
#         diff = np.abs(data1-data2)
#         y = diff
#         x = motion
#         slope, intercept, r_value, p_value, std_err = stats.linregress(x,y)
#         line = slope*np.array(x) + intercept
#         plt.plot(x,line,'r-',x,y,'ok')
#         plt.title('%s (%s: %.2f), r=%.2f'%(roi,task,t,r_value))
#         if r==(len(plot_rois)-2):
#             plt.ylabel('CBF abs difference (O1-O2)')
#             plt.xlabel('Total movement (cm)')
#     plt.tight_layout()