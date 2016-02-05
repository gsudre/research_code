# Function to write file for SAM covariate analysis
# by Gustavo Sudre, July 2014
import numpy as np
import os, sys
home = os.path.expanduser('~')
lib_path = os.path.abspath(home+'/research_code/meg/')
sys.path.append(lib_path)
import find_good_segments as fg


ds = sys.argv[1]
subj_name = ds.split('/')[-2].split('_')[0]
last = 240 #s
first = 0 #s
sf = 600 #hz
out_fname = ds + '/SAM/good_data'
time = np.arange(first, last, 1/float(sf))
markers_fname = home+'/data/meg/marker_data_clean.npy'
markers = np.load(markers_fname)[()]
idx = fg.get_good_indexes(markers[subj_name], time)
b = fg.group_consecutives(time[idx],step=np.round(1/float(sf),decimals=3))
fid = open(out_fname, 'w')
fid.write('%d\n'%len(b))
for t in b:
    fid.write('_time_\t%.3f\t%.3f\n'%(t[0],t[-1]))
fid.close()