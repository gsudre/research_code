''' Removes the appropriate volumes from TORTOISe files so that it can easily be processed by DIFFCALC or DIFFPREP later '''

import numpy as np
import re
import sys


# maskid = 1189
# rm_me = [40, 48, 51, 59, 60, 69, 77]

maskid = int(sys.argv[1])
rm_me = [int(i) for i in sys.argv[2:]]

root_fname = 'edti_DMC'

path = '/mnt/shaw/data_by_maskID/%04d/edti_proc/' % maskid

# update data .path file. Only include entries for volumes we
# are not removing
fid = open(path + '%s_DR.path' % root_fname, 'w')
lines = np.recfromtxt(path + '%s.path' % root_fname)
for l in lines:
    nvol = int(l.split('.')[-1])
    if nvol not in rm_me:
        fid.write(l + '\n')
fid.close()

# the noise.path file apparently gets indexed with new indexes
volumes = [int(sl.split('.')[-1]) for sl in lines if sl.find('SL0001') > 0]
ngood = len(volumes) - len(rm_me)
slices = np.unique([s.split('/')[-2] for s in lines])
fid = open(path + '%s_DR_noise.path' % root_fname, 'w')
for s in slices:
    for i in range(1, ngood + 1):
        fid.write('edti_DMC_noise_info/%s/I.%04d\n' % (s, i))
fid.close()

# removing the rows from the Bmatrix. Not identical to TORTOISE's, but might do the trick
bm = np.recfromtxt(path + '%s.bmtxt' % root_fname)
bm2 = np.delete(bm, np.array(rm_me) - 1, axis=0)
np.savetxt(path + '%s_DR.BMTXT' % root_fname, bm2, fmt='%6f')

# correct the entries in the .list file
fin = open(path + '%s.list' % root_fname, 'r')
fout = open(path + '%s_DR.list' % root_fname, 'w')
for line in fin:
    line = line.replace('<nim>%d</nim>' % len(volumes),
                        '<nim>%d</nim>' % ngood)
    line = line.replace(root_fname, root_fname + '_DR')
    line = line.replace('bmtxt', 'BMTXT')
    # we don't do any processing, so it's ok to just copy the original noise estimates
    if line.find('<noise_stdev_ori>') == 0:
        match = re.search(r'(\d+\.?\d+)', line)
        stdev_str = '<!-- NOISE_STDEV -->\n' + \
                    '<noise_stdev>%s</noise_stdev>' % match.group(0)
    if line.find('<noise_rms_ori>') == 0:
        match = re.search(r'(\d+\.?\d+)', line)
        rms_str = '<!-- NOISE_RMS -->\n' + \
                  '<noise_rms>%s</noise_rms>' % match.group(0)
    if line.find('<noise_mean_ori>') == 0:
        match = re.search(r'(\d+\.?\d+)', line)
        mean_str = '<!-- NOISE_MEAN -->\n' + \
                   '<noise_mean>%s</noise_mean>' % match.group(0)
    fout.write(line)
fout.write('\n%s\n' % stdev_str)
fout.write('\n%s\n' % rms_str)
fout.write('\n%s\n' % mean_str)
fin.close()
fout.close()
