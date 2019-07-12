# Grabs the results from CTSEM univariate analysis and formats it into .nii
# files.
import os
import subprocess
from scipy import stats
import numpy as np
import pandas as pd
import sys
import glob
home = os.path.expanduser('~')

res_fname = sys.argv[1]
mask_fname = sys.argv[2]
ijk_fname = sys.argv[3]
msgs_fname = sys.argv[4]


# write each column to its individual text file, and create the final nifti
def write_nifti(res, suffix=''):
    # file by concatenating each individual one
    for c in range(res.shape[1]):
        np.savetxt('./res%d.1D' % c, res[:, c])
        cmd_line = '1dcat -ok_1D_text %s ./res%d.1D' % (
            ijk_fname, c) + ' > ./tmp%d.1D' % (c)
        os.system(cmd_line)
        cmd_line = 'cat ./tmp%d.1D ' % (c) + \
                   '| 3dUndump -master %s -mask %s' % (mask_fname,
                                                       mask_fname) + \
                   ' -datum float -prefix ./res%d.nii.gz' % (c) + \
                   ' -overwrite -'
        os.system(cmd_line)
    res_str = ' '.join(
        ['./res%d.nii.gz' % (c) for c in range(res.shape[1])])
    out_fname = res_fname.replace('.csv', '%s.nii.gz' % suffix)
    cmd_line = '3dbucket -prefix %s %s' % (out_fname, res_str)
    os.system(cmd_line)
    cmd_line = 'rm %s ./res*1D ./tmp*' % (res_str)
    os.system(cmd_line)


# keep track of what voxels crapped out
run_again = []

# figure out how many voxels we're expecting
cmd_line = '3dBrickStat -sum %s' % mask_fname
nvox = 32#int(subprocess.check_output(cmd_line, shell=True).rstrip())

df = pd.read_csv(res_fname, header=None)
msgs = pd.read_csv(msgs_fname, header=None)

# since I'll need to output the voxels that didn't run anyways, let's go brute
# force here
# the results will be estimate, 1-pvalue, zscore, and everything else we use to
# calculate it: std, ub, lb
print('Compiling voxel results')
res = np.empty([nvox, 6])
res[:] = np.nan
for v in range(nvox):
    idx = df[6] == 'Y%d' % (v + 1)
    if any(idx):
        est = df[idx][1].iloc[0]
        sderr = df[idx][3].iloc[0]
        z = float(est) / float(sderr)
        # 2-sided p-value
        p = stats.norm.sf(abs(z))*2
        res[v, 0] = est
        res[v, 1] = 1-p
        res[v, 2] = z
        res[v, 3] = sderr
        res[v, 4] = df[idx][0].iloc[0]
        res[v, 5] = df[idx][2].iloc[0]
    else:
        run_again.append(f'Y{v+1}')

if len(run_again) == 0:
    write_nifti(res)

    print('Compiling masking results')
    imna = np.empty([nvox, ])
    imna[:] = np.nan
    for v in range(nvox):
        idx = msgs[6] == 'Y%d' % (v + 1)
        est = msgs[idx][1].iloc[0]
        # if the value is NA, then it ran fine!
        if type(est) == str:
            imna[v] = 1
        else:
            imna[v] = 0
    print(f'Need to mask {np.sum(imna) * 100.0 / nvox}% of voxels.')

    # first approach we just replace any voxels to be masked with a crappy
    # p-value and estimate
    idx = np.nonzero(imna)[0]
    res[idx, 0] = 0
    res[idx, 1] = 0
    write_nifti(res, suffix='_maskZero')

    # second approach with impute the estimates and stderrors we're masking, and
    # re-calculate the p-values

else:
    print(f'Voxels not found: {len(run_again)}')
    fout_name = './vlist_rerun.' + res_fname.split('/')[-1].replace('.csv', '')
    print(f'Creating re-run file {fout_name}')
    fid = open(fout_name, 'w')
    for v in run_again:
        fid.write('%s' % (v) + '\n')
    fid.close()
