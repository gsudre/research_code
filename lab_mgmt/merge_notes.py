''' Merges the notes form the Neuropsych spreadsheet front page to their respective entry in mr_records. Both have been previously converted to tab-limited files. '''
import numpy as np
import datetime as dt

visit_file = '/Users/sudregp/tmp/visit_records.txt'
tests_file = '/Users/sudregp/tmp/neuro_tests.txt'
# columns storing the data in each file
nnote = 112
nmrn = 0
ndate = 4
vnote = -1
vmrn = 0
vdate = 1

visits = np.recfromtxt(visit_file, delimiter='\t')
neuro = np.recfromtxt(tests_file, delimiter='\t')

# for each test record, find the corresponding visit
for rec in neuro[3:]:  # skipping headers
    # but first, check whether there is a note to be merged
    if len(rec[nnote]) > 0:
        mrn = int(rec[nmrn])
        date = dt.datetime.strptime(rec[ndate], '%m/%d/%y')
        vrow = [i for i in range(1, visits.shape[0])  # skipping headers
                if mrn == int(visits[i][vmrn]) and
                date == dt.datetime.strptime(visits[i][vdate], '%m/%d/%y')]
        if len(vrow) == 0:
            print 'ERROR: Could not find', mrn, 'on', date
        else:
            # removing ""
            if len(visits[vrow[0]][vnote]) > 0:
                note = visits[vrow[0]][vnote].replace('\"', '') + '. ' + rec[nnote].replace('\"', '')
            else:
                note = rec[nnote].replace('\"', '')
            print 'Adding note for', mrn, 'on', date, ':', note
            visits[vrow[0]][vnote] = note
np.savetxt(visit_file[:-4] + '2.txt', visits, fmt='%s', delimiter='\t')
