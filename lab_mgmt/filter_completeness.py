import numpy as np
import datetime as dt
import csv

fname = '/Users/sudregp/tmp/completenessUpTo12132013.txt'
dates = {'IQ': [14, 15, 16, 20, 21], 'ClinicalInterview': [17, 18, 19]}  
test_names = {'IQ': ['WPPSI-III', 'WASI-II', 'WASI-I', 'WTAR', 'WPPSI-IV'],
              'ClinicalInterview': ['SCID', 'DICA', 'CAADID']}

# figure out the last column that has data to be copied without cleaning
last_data = np.min([np.min(col) for col in dates.itervalues()])
clean_data = []
data = np.recfromtxt(fname, delimiter='\t')
maskids = np.unique([rec[0] for rec in data])
maskids = maskids[:-1]  # removing the title of the column
for m in maskids:
    mask_data = []
    # finds all rows for this specific mask id
    rows = [i for i in range(len(data)) if data[i][0]==m]
    mask_data = [str(i) for i in data[rows[0]][:last_data]]
    for test, cols in dates.iteritems():
        # look at all dates that we have for this test, and select the one that is closer to the scan date
        scan_date = dt.datetime.strptime(data[rows[0]][3], '%m/%d/%Y')
        test_dates = []
        for c in range(len(cols)):
            for r in rows:
                if len(data[r][cols[c]])>0:
                    test_dates.append([test_names[test][c], 
                                       dt.datetime.strptime(data[r][cols[c]], '%m/%d/%Y')])
        # if there are no dates for any tests, add a blank string
        if len(test_dates) > 0:
            date_diffs = []
            for d in test_dates:
                date_diffs.append(abs(scan_date-d[1]))
            mask_data.append(test_dates[np.argmin(date_diffs)][0])
            mask_data.append(np.min(date_diffs).days/30.)
        else:
            mask_data.append('')
            mask_data.append('')

    clean_data.append(mask_data)

# adding titles back to list
title = [str(i) for i in data[0][:last_data]]
for test in dates:
    title.append('Last %s' % test)
    title.append('Months between %s and scan' % test)
clean_data = [title] + clean_data
# writing to csv file
fout = open(fname[:-4] + '_clean.csv', 'w')
wr = csv.writer(fout)
wr.writerows(clean_data)
fout.close()
