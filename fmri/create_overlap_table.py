# outputs a table to summarizing the overlap between MEG and fMRI results
import os
home = os.path.expanduser('~')
import glob
import numpy as np

data_dir = home + '/data/results/Yeo_seeds_combined/'
res_files = glob.glob(data_dir + '/net*.txt')
out_file = data_dir + '/overlap_a0.01t0.99d5p5000.csv'

table = []
table.append(['seed','test','band','num voxels','fmri pct','meg pct'])
for fname in res_files:
    print fname
    data = np.genfromtxt(fname)
    nfmri = np.sum(data[:,6]>0)
    nmeg = np.sum(data[:,7]>0)
    noverlap = np.sum(data[:,8]>0)
    file_info = fname.split('/')[-1].split('_')
    table.append([file_info[0]+'_'+file_info[1], file_info[2], file_info[3], 
                  '%d'%noverlap, '%.2f'%(noverlap/float(nfmri)), 
                  '%.2f'%(noverlap/float(nmeg))])
fid = open(out_file,'w')
for row in table:
    fid.write(','.join(row) + '\n')
fid.close()
