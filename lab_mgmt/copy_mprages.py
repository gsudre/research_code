''' Goes through all the MR data in a list of mask ids, and copy the last MPRAGE data to a specific folder. Usage: copy_mprages.py list.txt out_dir/ '''

import glob
import re
import shutil
import sys


maskid_file = sys.argv[1]
copy_to = sys.argv[2] + '/%04d/'

fid = open(maskid_file, 'r')
copied_cnt = 0
cnt = 0
for maskid in fid:
    cnt += 1
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

    num_mprages = len(mprage_dirs)
    if num_mprages>0:
        if num_mprages==1:
            scan_num = 0
        else:
            print 'Found %d scans for %s.'%(num_mprages,maskid.rstrip())
            scan_num = 0
            while scan_num < 1:
                try:
                    scan_num=int(raw_input('Which scan to use?: '))
                except ValueError:
                    print "Not a number"
            scan_num -= 1
        mprage = mprage_dirs[scan_num]
        print 'Copying', maskid.rstrip(), 'to', copy_to%int(maskid.rstrip())
        shutil.copytree(mprage, copy_to%int(maskid))
        copied_cnt += 1
    else:
        print 'Did not find MPRAGE for', maskid

fid.close()

print '=== SUMMARY ==='
print 'Copied %d mask ids, %d not found.'%(copied_cnt, cnt-copied_cnt)