''' Goes through all the MR data in a list of mask ids, and copy the MPRAGE data to a specific folder '''

import glob
import re
import shutil


copy_to = '/mnt/v3/philip3T/raw_dicoms_NCR_MASKIDS/%04d'
maskid_file = '/Users/sudregp/tmp/maskids.txt'

fid = open(maskid_file, 'r')
for maskid in fid:
    maskid_dir = '/mnt/neuro/data_by_maskID/%04d/'%int(maskid)
    # we could have more than one date directory inside the same mask ID when there were two scan sessions (e.g. the first one was interrupted). Still they'll share the same date!
    date_dirs = glob.glob(maskid_dir + '/20*')

    mprage_dirs = []
    for date_dir in date_dirs:
        # get the name of the text file
        txtfile = glob.glob(date_dir + '/README*.txt')
        # find the line that has the word 'rage', then parse out the name of the folder that contains the data
        fid = open(txtfile[0])
        for line in fid:
            # not all MPRages start with prage, and rage by itself can match Storage
            if (line.lower().find('rage_') > 0) or (line.lower().find('mprage') > 0):
                m_obj = re.search("Series:(\S+)", line)
                # ignore any commas we might end up selecting
                if m_obj.group(1)[-1] == ',':
                    series_num = m_obj.group(1)[:-1]
                else:
                    series_num = m_obj.group(1)
                mprage_dirs.append(date_dir + '/' + series_num + '/')

    # always copy the last scan
    mprage = mprage_dirs[-1]
    print 'Copying', maskid, 'to', copy_to%int(maskid)
    shutil.copytree(mprage, copy_to%int(maskid))

fid.close()