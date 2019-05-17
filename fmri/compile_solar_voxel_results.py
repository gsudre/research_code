# Grabs the results from SOLAR univariate analysis and formats it into .nii
# files.
import os
import numpy as np
import sys
import glob
home = os.path.expanduser('~')

if len(sys.argv) > 1:
    analysis = sys.argv[1]
else:
    analysis = 'phen_3min_net06'

dir_name = home + '/data/tmp/'
out_fname = dir_name + 'polygen_results_%s.nii' % analysis
mask_root = home + '/data/heritability_change/fancy_mask_ijk'

# keep track of what voxels crapped out
run_again = []

folder = dir_name + analysis
voxel_folders = glob.glob(folder + '/v*_polygenic.out')
nvoxels = 154058 # 116483  # len(voxel_folders)

# the results are: h2r, h_pval, h2r_se, c2, c2_pval, high_kurtosis
res = np.empty([nvoxels, 6])
res[:] = np.nan
for v in range(nvoxels):
    if (v % 100) == 0:
        print v, '/', nvoxels
    fname = dir_name + analysis + '/v%05d_polygenic.out' % (v + 1)
    if not os.path.exists(fname):
        print 'ERROR: Could not find results for voxel %d' % (v + 1)
        run_again.append(v + 1)
    else:
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

print '\n\n %d/%d voxels crapped out\n\n' % (len(run_again), nvoxels)

if len(run_again) == 0:
    # write each column to its individual text file, and create the final nifti
    # file by concatenating each individual one
    for c in range(res.shape[1]):
        np.savetxt(dir_name + '/%s_res%d.1D' % (analysis, c), res[:, c])
        cmd_line = '1dcat -ok_1D_text %s_ijk.txt %s/%s_res%d.1D' % (
            mask_root, dir_name, analysis, c) + ' > %s/%s_tmp%d.1D' % (dir_name, analysis, c)
        os.system(cmd_line)
        cmd_line = 'cat %s/%s_tmp%d.1D ' % (dir_name, analysis, c) + \
                   '| 3dUndump -master %s.nii -mask %s.nii' % (mask_root,
                                                               mask_root) + \
                   ' -datum float -prefix %s/%s_res%d.nii.gz' % (dir_name, analysis, c) + \
                   ' -overwrite -'
        os.system(cmd_line)
    res_str = ' '.join(
        ['%s/%s_res%d.nii.gz' % (dir_name, analysis, c) for c in range(res.shape[1])])
    cmd_line = '3dbucket -prefix %s %s' % (out_fname, res_str)
    os.system(cmd_line)
    cmd_line = 'rm %s %s/%s_res*1D %s/%s_tmp*' % (res_str, dir_name, analysis, dir_name, analysis)
    os.system(cmd_line)
else:
    fout_name = home + '/solar_logs/rerun_%s.swarm' % analysis
    print 'Creating re-run file %s' % fout_name
    fid = open(fout_name, 'w')
    for v in run_again:
        fid.write('bash ~/research_code/run_solar_voxel.sh %s %d' % (analysis,
                  v) + '\n')
    fid.close()
