import numpy as np
import datetime as dt
import sys

if len(sys.argv)<8:
    print '\nWrong number of arguments!\n'
    print 'USAGE: python merge_on_closest_date.py file1.txt DateColumn1', \
            'MRNColumn1 file2.txt DateColumn2 MRNColumn2', \
            'mergedFileName.txt [removeNonMatched]\n'
    print 'NOTE: \n(1) The TXT files should be Tab delimited files.', \
          '\n(2) The column numbers are 0-based (i.e. the first column is 0)'
    sys.exit()
else:
    fname1 = sys.argv[1]
    date1 = int(sys.argv[2])
    mrn1 = int(sys.argv[3])
    fname2 = sys.argv[4]
    date2 = int(sys.argv[5])
    mrn2 = int(sys.argv[6])
    out_file = sys.argv[7]
    if len(sys.argv)==9:
        removeNonMatched = bool(int(sys.argv[8]))
    else:
        removeNonMatched = True

# # Use Tab-delimited files because we will evetually have notes section that include commas
# fname1 = '/Users/sudregp/data/motor/gf_tilApril3rd_scan.txt'
# date1 = 3
# mrn1 = 4
# fname2 = '/Users/sudregp/data/motor/gf_tilApril3rd_mb.txt'
# date2 = 11
# mrn2 = 0
# out_file = '/Users/sudregp/tmp/merged.txt'


''' Prints warnings to the screen when we found invalid MRNs in a data matrix, or invalid dates. Remove them from the data as well so we don't run into trouble later '''
def clean_up(data, mrn_idx, date_idx):
    remove_rows = []
    for i in range(len(data)):
        try:
            int(data[i][mrn_idx])
        except ValueError:
            print data[i][mrn_idx], 'is not a valid MRN! (row %d)'%(i+2)
            remove_rows.append(i)
        else:   
            if len(data[i][date_idx])==0:
                print 'Empty date field in (row %d)'%(i+2)
                remove_rows.append(i)
            else:
                try:
                    mydate = dt.datetime.strptime(data[i][date_idx], '%m/%d/%y')
                    data[i][date_idx] = dt.datetime.strftime(mydate,'%m/%d/%Y')
                except:
                    try:
                        dt.datetime.strptime(data[i][date_idx], '%m/%d/%Y')
                    except:
                        print data[i][date_idx], 'is not a valid date!',\
                              ' (row %d)'%(i+2)
                        remove_rows.append(i)
    data = np.delete(data, remove_rows, axis=0)
    return data


data1 = np.recfromtxt(fname1, delimiter='\t')
data2 = np.recfromtxt(fname2, delimiter='\t')
hdr1 = data1[0]
hdr2 = data2[0]

# let's do a series of quick checks to clean up the data
data1 = clean_up(data1[1:], mrn1, date1)
data2 = clean_up(data2[1:], mrn2, date2)

merged_data = []
# do this for rows in data1
for row in range(len(data1)):
    # store row indexes in data2 that match the current mrn
    matching_rows = [i for i in range(len(data2)) 
                       if int(data1[row][mrn1])==int(data2[i][mrn2])]
    row_date = dt.datetime.strptime(data1[row][date1], '%m/%d/%Y')
    # if we find the current MRN in data2
    if len(matching_rows) > 0:
        # figure out which row has a date that's closest to data1's date
        matching_dates = [dt.datetime.strptime(data2[i][date2], '%m/%d/%Y')
                          for i in matching_rows]
        date_diffs = [row_date-i for i in matching_dates]
        selected_row = matching_rows[np.argmin(np.abs(date_diffs))]
        date_difference = np.min(date_diffs).days/30.

        # now we merge the data from both spreadsheets
        merged_row = [i for i in data1[row]] + \
                     [i for i in data2[selected_row]] + \
                     [date_difference]
        merged_data.append(merged_row)
    else:
        print 'WARNING: Did not find any matching data for', \
               data1[row][mrn1], 'on', \
               dt.datetime.strftime(row_date,'%m/%d/%Y')
        if not removeNonMatched:
            merged_data.append([i for i in data1[row]])

print '\n\nFound %d matching records.\nWriting to %s'%(len(merged_data),out_file)

# writing output to TXT file
hdr = [i for i in hdr1] + [i for i in hdr2] + ['File1Date - File2Date (months)']
fid = open(out_file, 'w')
fid.write('\t'.join(hdr))
fid.write('\n')
for row in merged_data:
    str_row = [str(i) for i in row]
    fid.write('\t'.join(str_row))
    fid.write('\n')
fid.close()
