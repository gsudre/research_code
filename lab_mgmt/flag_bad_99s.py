''' Goes through all the MR data in a list of mask ids, and copy flags the mask ids that had something between the 99 scan and the dtis '''

import glob


maskid_file = '/Users/sudregp/tmp/mm.txt'

fid = open(maskid_file, 'r')
cnt99 = 0
cnt_bad = 0
cnt_mask_id = 0
for maskid in fid:
    cnt_mask_id += 1
    maskid_dir = '/mnt/neuro/data_by_maskID/%04d/'%int(maskid)
    # we could have more than one date directory inside the same mask ID when there were two scan sessions (e.g. the first one was interrupted). Still they'll share the same date!
    date_dirs = glob.glob(maskid_dir + '/20*')

    for date_dir in date_dirs:
        # get the name of the text file
        txtfile = glob.glob(date_dir + '/README*.txt')
        # reads the file into a list of strings
        scan_fid = open(txtfile[0])
        lines = scan_fid.readlines()

        # if we find a 99, make sure that the scan before was eDTI.
        for i in range(len(lines)):
            if lines[i].find('list99') > 0:
                cnt99 += 1
                if lines[i-1].find('dti') < 0:
                    print maskid
                    cnt_bad +=1
        scan_fid.close()
fid.close()
print 'Scans with 99:', cnt99, '/', cnt_mask_id
print 'Scan with 99 without preceding eDTI:', cnt_bad