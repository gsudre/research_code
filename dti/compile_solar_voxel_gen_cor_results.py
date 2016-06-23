# Grabs the results from SOLAR bivariate analysis and formats it into .nii
# files.
import os
import numpy as np
import sys
import glob
home = os.path.expanduser('~')

if len(sys.argv) > 1:
    analysis = sys.argv[1]
else:
    analysis = '00_fa_right_cst'

dir_name = home + '/data/tmp/'
out_fname = dir_name + 'polygen_results_%s.nii' % analysis
mask_root = home + '/data/fmri_example11_all/555/brain_mask_555'

# keep track of what voxels crapped out
run_again = []

folder = dir_name + analysis
voxel_folders = glob.glob(folder + '/v*_polygenic.out')
nvoxels = len(voxel_folders)

# the results are: rhog, rhog_pval, rhoe, rhoe_pval, rhop
res = np.empty([nvoxels, 5])
res[:] = np.nan
for v in range(nvoxels):
    if (v % 100) == 0:
        print analysis, v, '/', nvoxels
    fname = dir_name + analysis + '/v%05d_polygenic.out' % (v + 1)
    if not os.path.exists(fname):
        print 'ERROR: Could not find results for voxel %d' % (v + 1)
        run_again.append(v + 1)
    else:
        fid = open(fname, 'r')
        for line in fid:
            if line.find('RhoG is') >= 0:
                res[v, 0] = float(line.split('is ')[-1].split(' ')[0])
            if line.find('RhoG different from zero') >= 0:
                res[v, 1] = line.split('= ')[-1].split(' ')[0]
            if line.find('RhoE is') >= 0:
                res[v, 2] = float(line.split('is ')[-1].split(' ')[0])
                res[v, 3] = float(line.split('= ')[-1])
            if line.find('Derived Estimate of RhoP') >= 0:
                res[v, 4] = float(line.split('is ')[-1].split(' ')[0])
        fid.close()

print '\n\n %d/%d voxels crapped out\n\n' % (len(run_again), nvoxels)

if len(run_again) == 0:
    # write each column to its individual text file, and create the final nifti
    # file by concatenating each individual one
    for c in range(res.shape[1]):
        np.savetxt(dir_name + '/res%d.1D' % c, res[:, c])
        cmd_line = '1dcat -ok_1D_text %s_ijk.txt %s/res%d.1D' % (
            mask_root, dir_name, c) + ' > %s/tmp%d.1D' % (dir_name, c)
        os.system(cmd_line)
        cmd_line = 'cat %s/tmp%d.1D ' % (dir_name, c) + \
                   '| 3dUndump -master %s.nii -mask %s.nii' % (mask_root,
                                                               mask_root) + \
                   ' -datum float -prefix %s/res%d.nii.gz' % (dir_name, c) + \
                   ' -overwrite -'
        os.system(cmd_line)
    res_str = ' '.join(
        ['%s/res%d.nii.gz' % (dir_name, c) for c in range(res.shape[1])])
    cmd_line = '3dbucket -prefix %s %s' % (out_fname, res_str)
    os.system(cmd_line)
    cmd_line = 'rm %s %s/res*1D %s/tmp*' % (res_str, dir_name, dir_name)
    os.system(cmd_line)
else:
    fout_name = home + '/solar_logs/rerun_%s.swarm' % analysis
    print 'Creating re-run file %s' % fout_name
    fid = open(fout_name, 'w')
    for v in run_again:
        ic = analysis.split('_')[0]
        prop = analysis.split('_')[1]
        fid.write('bash ~/research_code/run_solar_voxel_gen_corr.sh %s %s %d' % (ic, prop, v) + '\n')
    fid.close()
