# collects connectivity sphere metrics for all subjects
import os
import numpy as np
import pandas as pd
import statsmodels.formula.api as smf
from scipy import io
import sys


home = os.path.expanduser('~')
gf_fname = home + '/data/meg/gf.csv'
subjs_fname = home+'/data/meg/usable_subjects_5segs13p654_SAM.txt'
data_dir = home + '/data/meg/rois_spheres/'
bands = [[1, 4], [4, 8], [8, 13], [13, 30], [30, 55], [65, 100]]
method = sys.argv[1]

fid = open(subjs_fname, 'r')
subjs = [line.rstrip() for line in fid]
fid.close()
gf = pd.read_csv(gf_fname)

for band in bands:
    bname = '%d-%d' % (band[0], band[1])
    mats = []
    for s in subjs:
        print s, bname
        fname = data_dir + '%s_%s.npy' % (s, method)
        subj_data = np.load(fname)[()][bname]
        idx = np.triu_indices_from(subj_data, k=1)
        mats.append(subj_data[idx])
    corr_mats = np.array(mats)

    good_subjs = np.sum(~np.isnan(corr_mats), axis=0)
    good_voxels = good_subjs == len(subjs)
    corr_mats = corr_mats[:, good_voxels]

    print np.sum(good_voxels), 'good connections out of', len(good_voxels)
    out = {'corr_mats': corr_mats, 'subjs': subjs, 'good_voxels': good_voxels}
    io.savemat(data_dir + '%s_%s.mat' % (method, bname), out)