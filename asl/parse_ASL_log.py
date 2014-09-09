''' Script to parse the log from run_multiple_procPCASL.sh '''
import re
import operator
import numpy as np
import matplotlib.pyplot as plt
import os
home = os.path.expanduser('~')

maskid = '1389'
log_dir = home + '/data/results/asl/'
nvols = 23
tasks = ['vid1','vid2','tfree1','tfree2']

# the outer loop is based on the figure layout
plt.figure(figsize=(10, 12))
plt_cnt = 1
task_outliers = []
for task in tasks:
    fname = log_dir + '/log_%s_%s.txt'%(maskid,task) 
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
            
    # organizing label data into left and right matrices
    # transforms the dictionary into a list of tuples sorted by key
    label_data = sorted(label_data.iteritems(), key=operator.itemgetter(0))
    num_points = len(label_data[0][1])
    num_labels = len(label_data)/2
    x = np.array(thresh)
    for h in ('left','right'):
        plt.subplot(5,2,plt_cnt)
        y = np.empty([num_points, num_labels])
        cnt = 0
        names = []
        for key, vals in label_data:
            if key.find(h)==0:
                y[:, cnt] = np.array(vals)
                names.append(key.replace(h+'-',''))
                cnt += 1
        
        plt.plot(x, y)
        plt.title('%s: %s (%s)'%(maskid, task, h))
        plt.xticks([])
        if plt_cnt==1:
            plt.ylabel('CBF')
        else:
            plt.ylabel('')
        plt_cnt += 1
    task_outliers.append(outliers)

# plotting the bottom two subplots
plt.subplot(5,2,plt_cnt)
y2 = np.array(task_outliers).T
plt.plot(x, y2, linewidth=2)
plt.ylabel('Pct of good volumes')
plt.xlabel('Threshold')
plt.title('Time points (data) used')
plt.legend(tasks,loc='lower right',ncol=1,fontsize='x-small')

plt.subplot(5,2,plt_cnt+1)
plt.plot(x, y, linewidth=2)
plt.legend(names,loc='center',ncol=2,fontsize='x-small')

plt.show()
