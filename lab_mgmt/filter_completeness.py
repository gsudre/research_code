''' Run in Qiagram completeness_v2 first, and change the column indexes below properly. Save the Qiagram results as a Tab delimited file. '''

import numpy as np
import datetime as dt
import csv

fname = '/Users/sudregp/Downloads/Results 11.txt'
scan_date_idx = 6
# last column before tests and interviews
last_clean_column_idx = 13
test_dates = {'IQ': [15, 17, 30, 32, 34], 'ClinicalInterview': [20, 23, 28]}  
# in the same order as specified in test_names, the the order according to test_data_names
test_data = {'IQ': [[14], [16], [29], [31], [33]], 
            'ClinicalInterview': [[18, 19], [21, 22], [24, 25, 26, 27]]}
test_names = {'IQ': ['WASI-II', 'WASI-I', 'WTAR', 'WPPSI-IV', 'WPPSI-III'], 'ClinicalInterview': ['ClinicallyAdministeredSX', 'DICA', 'CAADID']}
test_data_names = {'IQ': ['FSIQ'], 'ClinicalInterview': ['Inattention','HI','Inattention (past)','HI (past)']}


clean_data = []
data = np.recfromtxt(fname, delimiter='\t')
maskids = np.unique([rec[0] for rec in data])
maskids = maskids[:-1]  # removing the title of the column
for m in maskids:
    mask_data = []
    # finds all rows for this specific mask id
    rows = [i for i in range(len(data)) if data[i][0]==m]
    mask_data = [str(i) for i in data[rows[0]][:last_clean_column_idx]]
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
                date_diffs.append(abs(scan_date-d[1]))
            tname = my_test_dates[np.argmin(date_diffs)][0]
            mask_data.append(tname)
            mask_data.append(np.min(date_diffs).days/30.)
            tdata = my_test_dates[np.argmin(date_diffs)][2]
            for d in tdata:
                mask_data.append(d)
        # if there are no dates for any tests, add a blank string
        else:
            mask_data.append('')
            mask_data.append('')

    clean_data.append(mask_data)

# adding titles back to list
title = [str(i) for i in data[0][:last_clean_column_idx]]
for test in test_dates:
    title.append('Last %s' % test)
    title.append('Months between %s and scan' % test)
    for d in test_data_names[test]:
        title.append(d)
clean_data = [title] + clean_data
# writing to csv file
fout = open(fname[:-4] + '_clean.csv', 'w')
wr = csv.writer(fout)
wr.writerows(clean_data)
fout.close()
