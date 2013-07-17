''' Extracts the dates from the MR_records file that correspond to the MRN in the Biosamples file. Outputs it to the screen so we can later copy it to the file.'''
import numpy as np
import datetime as dt


def unique(seq):
    seen = set()
    seen_add = seen.add
    return [ x for x in seq if x not in seen and not seen_add(x)]


bio_file = '/Users/sudregp/Documents/amy/Biosamples_Labmatrix_v3.txt'
mr_file = '/Users/sudregp/Documents/amy/MR_records_Labmatrix.txt'
mr15_file = '/Users/sudregp/Documents/amy/mr_records_15T_ADHD_NV_scans_2011_06_27.txt'
ocd_file = '/Users/sudregp/Documents/amy/scans_15T_ADD_ADT_OCD_NV_2011_06_27.txt'
nvt_file = '/Users/sudregp/Documents/amy/scans_15T_NVT_2011_06_30.txt'

# columns storing the data in each file
bmrn = 0
mmrn = 0
mdate = 8
m15mrn = 5
m15date = 8
omrn = 4
odate = 6
nmrn = 2
ndate = 4

bio = np.recfromtxt(bio_file, delimiter='\t')
mr = np.recfromtxt(mr_file, delimiter='\t')
mr15 = np.recfromtxt(mr15_file, delimiter='\t')
ocd = np.recfromtxt(ocd_file, delimiter='\t')
nvt = np.recfromtxt(nvt_file, delimiter='\t')

# for each bio record, find the corresponding visit
for rec in bio[1:]:  # skipping headers
    mrn = int(rec[bmrn])
    mrow = [i for i in range(1, mr.shape[0]) if mrn == int(mr[i][mmrn])]
    m15row = [i for i in range(1, mr15.shape[0]) if mrn == int(mr15[i][m15mrn])]
    orow = [i for i in range(1, ocd.shape[0]) if mrn == int(ocd[i][omrn])]
    nrow = [i for i in range(1, nvt.shape[0]) if mrn == int(nvt[i][nmrn])]
    if len(mrow + m15row + orow + nrow) == 0:
        print mrn, '\tERROR: Could not find record anywhere!'
    else:
        a = []
        for i in mrow:
            a.append(mr[i][mdate])
        for i in m15row:
            a.append(mr15[i][m15date])
        for i in orow:
            a.append(ocd[i][odate])
        for i in nrow:
            a.append(nvt[i][ndate])
        print mrn, '\t', '\t'.join(unique(a))
