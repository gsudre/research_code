''' Goes through all the MR data and, for the subjects we have MPRAGE data, create a MINC version that is renamed to match the mask ID '''

import glob
import os
import re
import shutil


path = '/mnt/neuro/MR_data/'
tmp_dir = '/tmp/minc_tmp/'
minc_final = '/tmp/minc_final/'

# start anew with the temporary folder
if os.path.isdir(tmp_dir):
    shutil.rmtree(tmp_dir)
os.mkdir(tmp_dir)

# get a list of the subjects in the server
subjs = glob.glob(path + '/*')
# filter the list for occurrences of eaDir
subjs = [x for x in subjs if x.find('@eaDir')<0]

for subj_dir in subjs:
    # look for all mask ids this subject has
    maskids = glob.glob(subj_dir + '/*')
    maskids = [x for x in maskids if x.find('@eaDir')<0]

    for maskid_dir in maskids:
        mask_id = int(maskid_dir.split('/')[-1])

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
                    mprage_dirs.append(date_dir + '/' + series_num + '/*dcm')

        for mprage in mprage_dirs:
            print mask_id, mprage
            # convert the data to MINC
            os.system('dcm2mnc ' + mprage + ' ' + tmp_dir)
            # rename the file
            minc_created = glob.glob(tmp_dir + '/*')[-1]
            res_file = glob.glob(minc_created + '/*mnc')[-1]
            fmt_maskid = '%04d' % mask_id
            shutil.move(res_file, minc_final + fmt_maskid + '_mprage.mnc')
            # remove the temporary dir
            os.rmdir(minc_created)
