''' Script to parse the log from run_multiple_procPCASL.sh '''
import re
import operator
import numpy as np
import matplotlib.pyplot as plt

fname = '/Users/sudregp/data/results/asl/log_1317_2.txt'
title_str = '1317 resting'

thresh = []
outliers = []
label_data = {}
fid = open(fname,'r')
waiting_for_value = False
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
            outliers.append(100*(1-float(obj.group(1))/23))
        obj = re.search('^::(\w+):(\w+)::', line)
        if obj is not None:
            label_name = obj.group(1) + '-' + obj.group(2)
            waiting_for_value = True
        
# organizing label data into left and right matrices
# transforms the dictionary into a list of tuples sorted by key
label_data = sorted(label_data.iteritems(), key=operator.itemgetter(0))
num_points = len(label_data[0][1])
num_labels = len(label_data)/2
x = np.array(thresh)
plt.figure(figsize=(10.2, 8.5))
plt_cnt = 1
for h in ('left','right'):
    y = np.empty([num_points, num_labels])
    cnt = 0
    names = []
    for key, vals in label_data:
        if key.find(h)==0:
            y[:, cnt] = np.array(vals)
            names.append(key.replace(h+'-',''))
            cnt += 1
    plt.subplot(3,1,plt_cnt)
    plt.plot(x, y)
    plt.plot(x, outliers, 'ko:')
    plt.title('%s %s'%(h, title_str))
    plt_cnt += 1
plt.xlabel('Threshold (fraction of outlier pixels)')
plt.ylabel('CBF')
plt.subplot(3,1,3)
plt.plot(x, y)
plt.legend(names,loc='center',ncol=2)
plt.show()

'''
voxels included
'''