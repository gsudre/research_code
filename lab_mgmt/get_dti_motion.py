''' Goes through all the edti_proc folders and calculates mean translation and rotation parameters per mask id '''

import glob
import os
import csv
import numpy as np


path = '/Volumes/neuro/MR_data/'

# get a list of the subjects in the server
subjs = glob.glob(path + '/*')

subj_movement = []

for subj_dir in subjs:
    # look for all mask ids this subject has
    maskids = glob.glob(subj_dir + '/*')
    for maskid_dir in maskids:
        # only continue if this subject has edti_proc
        if os.path.isdir(maskid_dir + '/edti_proc'):
            mask_id = int(maskid_dir.split('/')[-1])
            # find what's the name of the transformations folder
            trans_file = glob.glob(maskid_dir + '/edti_proc/*_rpd.transformations')
            if len(trans_file) > 0:
                print 'Working on', trans_file[-1]
                data = np.genfromtxt(trans_file[-1])
                mean_mvmt = np.mean(np.abs(data[:, :6]), axis=0)
                translation = np.sqrt(np.sum(mean_mvmt[:3]**2))
                rotation = np.sqrt(np.sum(mean_mvmt[3:]**2))
                subj_movement.append([mask_id] + list(mean_mvmt) + [translation, rotation])

table = [['mask id', 'meanX trans', 'meanY trans', 'meanZ trans', 'meanX rot', 'meanY rot', 'meanZ rot', 'norm trans', 'norm rot']]
table = table + subj_movement
fout = open('/Users/sudregp/tmp/mean_dti_movement.csv', 'w')
wr = csv.writer(fout)
wr.writerows(table)
fout.close()