# Script to check the alpha for each cluster in Bartholt's results
import os
import numpy as np
import glob


t = 1.96  # 1.96 or 2.58
rmm = -1
home = os.path.expanduser('~')
input_fname = home + '/data/bartholt/rh.smoothwm.asc'
#input_fname = '/mnt/shaw/freesurfer5.3_subjects/fsaverage2/SUMA/lh.smoothwm.asc'
# input_fname = home + '/data/bartholt/rh.smoothwm.asc'
res_fname = home + '/data/bartholt/rc_ordered.asc'
perm_dir = home + '/data/bartholt/perms/'
perm_root = 'rc_ordered_*.asc'
tmp_fname = 'junk%.2f.1D' % np.random.rand()

cmd_str = 'SurfClust -i %s -input %s 0 -rmm %f -thresh_col 0 -athresh %f -n 1 -sort_area -no_cent > %s' % (input_fname, res_fname, rmm, t, tmp_fname)
os.system(cmd_str)
# check the size of all clusters we have in the result
clusters = np.genfromtxt(tmp_fname)
if clusters.ndim == 1:
        clusters = clusters[np.newaxis, :]
nclusters = clusters.shape[0]
counts = np.zeros(nclusters)

# for each permutation, count how many clusters are bigger than each of our result clusters
files = glob.glob(perm_dir + perm_root)
for f, fname in enumerate(files):
    print 'Evaluating %d / %d' % (f + 1, len(files))
    cmd_str = 'SurfClust -i %s -input %s 0 -rmm %f -thresh_col 0 -athresh %f -n 1 -sort_area -no_cent > %s' % (input_fname, fname, rmm, t, tmp_fname)
    os.system(cmd_str)
    perm_clusters = np.genfromtxt(tmp_fname)
    if perm_clusters.ndim == 1:
        perm_clusters = perm_clusters[np.newaxis, :]
    for i in range(nclusters):
        if np.sum(perm_clusters[:, 2] >= clusters[i, 2]) > 0:
            counts[i] += 1
counts /= len(files)
