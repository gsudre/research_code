''' Script to parse the log from run_multiple_procPCASL.sh '''
import re

fname = '/Users/sudregp/tmp/log2.txt'

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
            outliers.append(float(obj.group(1))/23)
        obj = re.search('^::(\w+):(\w+)::', line)
        if obj is not None:
            label_name = obj.group(1) + '-' + obj.group(2)
            waiting_for_value = True
        
