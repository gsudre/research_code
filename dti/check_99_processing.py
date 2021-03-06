''' Goes through all the edti_proc in a file and checks what volumes were removed '''

import glob
import csv
import numpy as np
import os
import re


path = '/mnt/shaw/data_by_maskID/%04d/'
home = os.path.expanduser('~')

fname = home + '/tmp/en.txt'  # '/mnt/neuro/dti_longitudinal/nv_boys.txt'#sys.argv[1]
fid = open(fname, 'r')

data = []

for line in fid:
    maskid = int(line)
    print '%04d' % maskid
    notes = ''
    original_cdi = glob.glob(path % maskid + '/E*/cdiflist0*')[0]
    with open(original_cdi, 'r') as f:
        num_original_volumes = f.readline().rstrip()
    # store the indexes of replayed volumes
    replayed_vols = []
    cdi99 = glob.glob(path % maskid + '/E*/cdiflist99*')
    if len(cdi99) == 0:
        num_volumes99 = 0
        notes = notes + 'No resampled gradient file. '
    else:
        with open(cdi99[0], 'r') as f:
            # store the total number of replayed volumes
            num_volumes99 = f.readline().rstrip()
        replayed_cdi = glob.glob(path % maskid + '/E*/cdiflistOriginalAndReplayedCombined*')[0]
        with open(replayed_cdi, 'r') as f:
            replayed_volumes = f.readline().rstrip()
        replayed_info = glob.glob(path % maskid + '/E*/directionsReplayedInfo.txt')[0]
        fid = open(replayed_info, 'r')
        for line in fid:
            if line.find('Diffusion') == 0:  # has some text in it
                vol = int(line.split(':')[0].split(' ')[-1])
                replayed_vols.append(vol)
        fid.close()
    tortoise_original = path % maskid + '/edti_proc/edti.list'
    if not os.path.exists(tortoise_original):
        details = 'NA'
        remove_me = []
        notes = notes + 'Not imported in DIFFPREP: no edti.list. '
        tortoise_final = None
        vol_final = 0
        vol_imported = 0
    else:
        fid = open(tortoise_original, 'r')
        for line in fid:
            if line.find('<nim>') >= 0:
                match = re.search(r'(\d+)', line)
                vol_imported = int(match.group(0))
        fid.close()
        tortoise_final = path % maskid + '/edti_proc/edti_DMC_DR_R1.list'
        if not os.path.exists(tortoise_final):
            # there are no list files with volumes removed
            vol_final = int(num_original_volumes) + int(num_volumes99)
            details = 'NA'
            replayed_removed = 'N'
            remove_me = replayed_vols
            tortoise_final = path % maskid + '/edti_proc/edti_DMC_R1.list'
            if not os.path.exists(tortoise_final):
                # this is a problem, becaus they all should have robust processing!
                tortoise_final = path % maskid + '/edti_proc/edti_DMC.list'
                notes = notes + 'No robust processing. '
                if not os.path.exists(tortoise_final):
                    # haven't done much with this character
                    tortoise_final = None
                    num_removed = 'NA'
                    notes = notes + 'No DIFFCALC processing. '
        else:
            fid = open(tortoise_final, 'r')
            for line in fid:
                if line.find('<nim>') >= 0:
                    match = re.search(r'(\d+)', line)
                    vol_final = int(match.group(0))
            fid.close()

    if vol_final != int(num_original_volumes) + int(num_volumes99) and vol_final != 0:
        path_file = glob.glob(path % maskid + 'edti_proc/*DMC_DR_R1.path')
        slices = np.recfromtxt(path_file[-1])
        # we only need to look at the first directory to figure out what slices are missing. It's repeated across directories
        good = [int(sl.split('.')[-1]) for sl in slices if sl.find('SL0001') > 0]
        details = list(np.setdiff1d(np.arange(1, vol_imported), good))
        replayed_removed = True
        for v in replayed_vols:
            if v not in details:
                replayed_removed = False

        if replayed_removed:
            replayed_removed = 'Y'
        else:
            replayed_removed = 'N'
            remove_me = np.unique(replayed_vols + details)
    else:
        replayed_removed = 'NA'

    if replayed_removed != 'Y':
        rm_str = ' '.join(['%d' % i for i in list(remove_me)])
    else:
        rm_str = ''

    rv_str = ' '.join(['%d' % i for i in replayed_vols])
    if details != 'NA':
        d_str = ' '.join(['%d' % i for i in details])
    else:
        d_str = details

    if int(vol_imported) != int(num_original_volumes) + int(num_volumes99):
        wrong_imported = 'Y'
    else:
        wrong_imported = 'N'

    data.append(['%04d' % maskid] + [num_original_volumes, num_volumes99,
                                     rv_str, vol_imported, wrong_imported,
                                     d_str, vol_final, replayed_removed,
                                     rm_str, notes])


table = [['mask id', 'original', 'replayed', 'volumes replayed (minus B0)',
          'imported', 'wrong imported', 'volumes removed', 'remaining',
          '99 removed', 'remove_list', 'notes']]
table = table + data
fout = open(home + '/tmp/99_info.csv', 'w')
wr = csv.writer(fout)
wr.writerows(table)
fout.close()
