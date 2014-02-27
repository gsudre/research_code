import shutil
import os

#### EDIT THESE VARIABLES AS YOU NEED ####
# use the symbol %04d to replace the variable mask id
copy_from = '/Volumes/neuro/cortical_civet/ncr_maskids/%04d/native/nih_chp_%04d_t1_nuc.mnc'
copy_to = '/Users/sudregp/tmp/'
# the list needs to be a TXT file! only one column of maskids, no header
maskid_list = '/Users/sudregp/tmp/grab_these.txt'


#### STARTING HERE, NOTHING NEEDS TO BE CHANGED ####
fid = open(maskid_list, 'r')
for line in fid:
    fname = copy_from % (int(line), int(line))
    if os.path.exists(fname):
        print 'Copying', fname
        shutil.copy(fname, copy_to)
    else:
        print 'ERROR: Could not find', fname

fid.close()