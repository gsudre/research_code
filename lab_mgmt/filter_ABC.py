''' Run in Qiagram ABC_data first, and change the column indexes below properly. Save the Qiagram results as a Tab delimited file. '''

import numpy as np
import datetime as dt
import csv

fname = '/Users/sudregp/Downloads/ABC_from_labmatrix4.txt'
data = np.recfromtxt(fname, delimiter='\t')

scan_date_idx = 7
# last column before data to be sorted
last_clean_column_idx = 13
# a quick way to check these indexes is to open the file in Python and do [i for i,tmp in enumerate(data[0]) if tmp.find('date')>0] or even ['%d:%s'%(i,tmp) for i,tmp in enumerate(data[0]) if tmp.find('Motor')>=0]
test_dates = {'IQ': [14, 18, 22, 26, 31], 'Beery VMI': [40], 'DCDQ': [61], 'Motor': [74]}  
# in the same order as specified in test_names, the order according to test_data_names. For the dict values, neew to have one list inside the main list for each date idx
test_data = {'IQ': [[15], [19], [23], [27], [32]], 
            'Beery VMI': [[37, 38, 39]],
            'DCDQ': [range(41, 61)],
            'Motor': [range(62, 74)]}
# as many as date indexes in each value of test_dates, indicating the test that is selected based on the closest date
test_names = {'IQ': ['WASI-I', 'WASI-II', 'WTAR', 'WPPSI-III', 'WPPSI-IV'], 'Beery VMI': ['Beery VMI'], 'DCDQ': ['DCDQ'], 'Motor': ['Motor']}
# as many as the length of the inner keys in test_date. We remove the last one to exclude the date field
test_data_names = {'IQ': ['FSIQ'], 
                    'Beery VMI': [s for s in data[0] if s.find('Beery')>=0][:-1],
                    'DCDQ': [s for s in data[0] if s.find('DCDQ')>=0][:-1],
                    'Motor': [s for s in data[0] if s.find('Motor')>=0][1:-1]
                    }

clean_data = []
maskids = np.unique([rec[0] for rec in data])
maskids = maskids[:-1]  # removing the title of the column
for m in maskids:
    mask_data = []
    # finds all rows for this specific mask id
    rows = [i for i in range(len(data)) if data[i][0]==m]
    mask_data = [str(i) for i in data[rows[0]][:(last_clean_column_idx+1)]]
    for test, cols in test_dates.iteritems():
        # look at all dates that we have for this test, and select the one that is closer to the scan date
        scan_date = dt.datetime.strptime(data[rows[0]][scan_date_idx], '%m/%d/%Y')
        my_test_dates = []
        for c in range(len(cols)):
            for r in rows:
                if len(data[r][cols[c]])>0:
                    tname = test_names[test][c]
                    tdate = dt.datetime.strptime(data[r][cols[c]], '%m/%d/%Y')
                    tindex = [i for i in range(len(test_names[test])) if test_names[test][i]==tname][0]
                    tdata = data[r][test_data[test][tindex]]
                    my_test_dates.append([tname, tdate, tdata])
        # add the name of the selected test, how much time difference between
        # test and scan, and the data for the test
        if len(my_test_dates) > 0:
            date_diffs = []
            for d in my_test_dates:
                date_diffs.append(scan_date-d[1])
            tname = my_test_dates[np.argmin(date_diffs)][0]
            mask_data.append(tname)
            mask_data.append(np.min(date_diffs).days/30.)
            tdata = my_test_dates[np.argmin(date_diffs)][2]
            for d in tdata:
                mask_data.append(d)
        # if there are no dates for any tests, add one blank string for each data value we were expecting, plus two (date and test name)
        else:
            for i in range(len(test_data[test][0])+2):
                mask_data.append('')

    clean_data.append(mask_data)

# adding titles back to list
title = [str(i) for i in data[0][:(last_clean_column_idx+1)]]
for test in test_dates:
    title.append('Last %s' % test)
    title.append('Difference in months (scan - %s)' % test)
    for d in test_data_names[test]:
        title.append(d)
clean_data = [title] + clean_data
# writing to csv file
fout = open(fname[:-4] + '_clean.csv', 'w')
wr = csv.writer(fout)
wr.writerows(clean_data)
fout.close()
