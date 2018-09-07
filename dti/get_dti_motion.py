''' Goes through all the edti_proc in a file and calculates mean translation
    and rotation parameters per mask id '''

import glob
import csv
import numpy as np
import os
import sys


path = '/Volumes/Shaw/data_by_maskID/%04d/edti_proc/'
home = os.path.expanduser('~')

fname = sys.argv[1]
fid = open(fname, 'r')

subj_movement = []
for line in fid:
    maskid = int(line)
    print(maskid)
    # find what's the name of the transformations folder
    trans_file = glob.glob(path % maskid + '/*rpd.transformations')
    if len(trans_file) > 0:
        print('Working on', trans_file[-1])
        data = np.genfromtxt(trans_file[-1])
        nvolumes = data.shape[0]
        # look for the path to all slices
        path_file = glob.glob(path % maskid + '/*DMC*_R1.path')
        if len(path_file) > 0:
            slices = np.recfromtxt(path_file[-1])
            # we only need to look at the first directory to figure out what
            # slices are missing. It's repeated across directories
            good = [int(sl.split('.')[-1]) for sl in slices
                    if sl.find('SL0001') > 0]
            # the .path file stores all volumes used for each slice in 1-base
            # matrices are zero-based
            good_idx = np.array(good) - 1
            removed = np.setdiff1d(np.arange(1, nvolumes), good)
            print('Good slices: %d/%d, Removed:' % (len(good),
                                                    nvolumes), list(removed))
            mean_mvmt = np.mean(np.abs(data[good_idx, :6]), axis=0)
            translation = np.sqrt(np.sum(mean_mvmt[:3]**2))
            rotation = np.sqrt(np.sum(mean_mvmt[3:]**2))
            # 1-based list of volumes removed
            removed_str = ';'.join(['%d' % d for d in list(removed)])
            # AFNI takes keep_str as 0 based!
            keep_str = ';'.join(['%d' % (d-1) for d in good])
            subj_movement.append(['%04d' % maskid] + list(mean_mvmt) +
                                [translation, rotation, nvolumes,
                                len(good), len(removed), removed_str, keep_str])
        else:
            print('\nWARNING: Did not find R1 .path file for', maskid, '\n')
    else:
        print('\nWARNING: Did not find transformation file for', maskid, '\n')
    if len(trans_file) > 1:
        print('\nWARNING! More than one transformation file for %d\n' % maskid)

table = [['mask id', 'meanX trans', 'meanY trans', 'meanZ trans',
          'meanX rot', 'meanY rot', 'meanZ rot', 'norm trans', 'norm rot',
          'numVolumes', 'goodVolumes', 'missingVolumes', 'removedVolumes', 'keepVolumes']]
table = table + subj_movement
fout = open(home + '/tmp/mean_dti_movement.csv', 'w')
wr = csv.writer(fout)
wr.writerows(table)
fout.close()
