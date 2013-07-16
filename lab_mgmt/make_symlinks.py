''' Generates symlinks for every mask ID. Should probably run it once in a while to generate the links for the new data, since the sort_data script DOES NOT do this! '''
import glob
import os


data_dir = '/Volumes/neuro/MR_data/'
target_dir = '/Volumes/neuro/data_by_maskID/'

subjects = glob.glob(data_dir + '/*')
for subj_dir in subjects:
    # find out all mask ids per subject
    mask_dirs = glob.glob(subj_dir + '/*')
    for mask_dir in mask_dirs:
        mask_id = mask_dir.split('/')[-1]
        subj_name = mask_dir.split('/')[-2]
        link_name = target_dir + ('%04.0d' % int(mask_id))
        source = '../MR_data/' + subj_name + '/' + mask_id
        if os.path.exists(link_name):
            print 'Error:', link_name, 'already exists!'
        else:
            os.symlink(source, link_name)
