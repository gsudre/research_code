''' Goes through all the MR data in a folder and creates a MINC version that is renamed to match the mask ID. The folder needs to be organized by mask id, and have DICOM files inside the mask id folder (i.e. as output by
    copy_mprages.py) '''

import glob
import os
import shutil
import sys


path = sys.argv[1]
tmp_dir = '/tmp/minc_tmp/'
minc_final = '/tmp/minc_final/'

# start anew with the temporary folder
if os.path.isdir(tmp_dir):
    shutil.rmtree(tmp_dir)
os.mkdir(tmp_dir)

# look for all mask ids in the folder
maskids = glob.glob(path + '/*')

for maskid_dir in maskids:
    print maskid_dir
    mask_id = int(maskid_dir.split('/')[-1])
    # convert the data to MINC
    os.system('dcm2mnc ' + maskid_dir + '/*dcm ' + tmp_dir)
    # rename the file
    minc_created = glob.glob(tmp_dir + '/*')[-1]
    res_file = glob.glob(minc_created + '/*mnc')[-1]
    fmt_maskid = '%04d' % mask_id
    shutil.move(res_file, minc_final + fmt_maskid + '_mprage.mnc')
    # remove the temporary dir
    os.rmdir(minc_created)
