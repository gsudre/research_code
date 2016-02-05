#! /usr/bin/env python
''' Generates symlinks for every mask ID. Only needs to be run in the creation of the folder, or if for some reason data_by_maskID gets deleted'''
import glob
import os


data_dir = '/mnt/shaw/MR_data/'
target_dir = '/mnt/shaw/data_by_maskID/'

subjects = glob.glob(data_dir + '/*')
for subj_dir in subjects:
    # find out all mask ids per subject
    mask_dirs = glob.glob(subj_dir + '/*')
    for mask_dir in mask_dirs:
        mask_id = mask_dir.split('/')[-1]
        subj_name = mask_dir.split('/')[-2]
        link_name = target_dir + ('%04.0d' % int(mask_id))
        source = '../MR_data/' + subj_name + '/' + mask_id
        if not os.path.exists(link_name):
            print 'Creating ', link_name
            os.symlink(source, link_name)
