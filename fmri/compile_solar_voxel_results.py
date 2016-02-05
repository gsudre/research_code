# Grabs the results from SOLAR univariate analysis and formats it into .nii files.
import os
import numpy as np
import nibabel as nb
import sys
home = os.path.expanduser('~')

if len(sys.argv) > 1:
    analysis = sys.argv[1]
else:
    analysis = 'IC02'

dir_name = home + '/data/solar_paper/'
out_fname = dir_name + 'polygen_results_%s.nii' % analysis

mask = nb.load(home + '/data/fmri_example11_all/555/brain_mask_555.nii')
# good voxels
gv = mask.get_data().astype(bool).flatten()
nvoxels = np.sum(gv)

# keep track of what voxels crapped out
run_again = []
# the results are: h2r, h_pval, h2r_se, c2, c2_pval, high_kurtosis
res = np.empty([nvoxels, 6])
res[:] = np.nan
for v in range(nvoxels):
    # print '%d / %d' % (v, nvoxels)
    folder = dir_name + analysis + '/v%d' % v
    if not os.path.exists(folder):
        print 'ERROR: Could not find results for voxel %d' % v
        run_again.append(v)
    else:
        fname = folder + '/polygenic.out'
        fid = open(fname, 'r')
        for line in fid:
            if line.find('H2r is') >= 0:
                h2r = float(line.split('is ')[-1].split(' ')[0])
                p = float(line.split('= ')[-1].split(' ')[0])
                res[v, 0] = h2r
                res[v, 1] = 1 - p
                # there's no SE when h2r is 0
                if h2r < 0.000000001:
                    res[v, 2] = 0
            if line.find('C2 is') >= 0:
                c2 = float(line.split('is ')[-1].split(' ')[0])
                # there's no p-value when c2 = 0
                if c2 < 0.000000001:
                    p = .5
                else:
                    p = float(line.split('= ')[-1].split(' ')[0])
                res[v, 3] = c2
                res[v, 4] = 1 - p
            if line.find('Residual Kurtosis') >= 0:
                if line.find('too high') > 0:
                    print 'Residual kurtosis too high for voxel %d' % v
                    res[v, 5] = 1
                else:
                    res[v, 5] = 0
            if line.find('H2r Std. Error:') >= 0:
                se = float(line.split(':')[-1])
                res[v, 2] = se
        fid.close()

print 'Creating file to run missing voxels again (%d / %d)' % (len(run_again), nvoxels)
fid = open(home + '/solar_logs/run_again_' + analysis + '.sh', 'w')
for v in run_again:
    fid.write('cd ~/data/solar_paper; solar run_ica_voxel %s %d' % (analysis.split('IC')[-1], v) + '\n')
fid.close()

data = np.zeros([len(gv), res.shape[-1]])
data[gv, :] = res
data = data.reshape(mask.get_data().shape[:3] + tuple([-1]))
nb.save(nb.Nifti1Image(data, mask.get_affine()), out_fname)
