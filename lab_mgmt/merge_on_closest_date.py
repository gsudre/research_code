import numpy as np
import datetime as dt

# Use Tab-delimited files because we will evet
fname1 = '/Users/sudregp/Documents/dan/CPTreformatted02122014.txt'
date1 = 8
mrn1 = 0
fname2 = '/Users/sudregp/Documents/dan/DICA 5-28-13 to go into labmatrix_fixed.txt'
date2 = 2
mrn2 = 0
out_file = '/Users/sudregp/tmp/merged.txt'


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
            try:
                dt.datetime.strptime(data[i][date_idx], '%m/%d/%y')
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
    row_date = dt.datetime.strptime(data1[row][date1], '%m/%d/%y')
    # if we find the current MRN in data2
    if len(matching_rows) > 0:
        # figure out which row has a date that's closest to data1's date
        matching_dates = [dt.datetime.strptime(data2[i][date2], '%m/%d/%y')
                          for i in matching_rows]
        date_diffs = [abs(row_date-i) for i in matching_dates]
        selected_row = matching_rows[np.argmin(date_diffs)]
        date_difference = np.min(date_diffs).days/30.

        # now we merge the data from both spreadsheets
        merged_row = [i for i in data1[row]] + \
                     [i for i in data2[selected_row]] + \
                     [date_difference]
        merged_data.append(merged_row)
    else:
        print 'WARNING: Did not find any matching data for', \
               data1[row][mrn1], 'on', \
               dt.datetime.strftime(row_date,'%m/%d/%y')

print '\n\nFound %d matching records.\nWriting to %s'%(len(merged_data),out_file)

# writing output to TXT file
hdr = [i for i in hdr1] + [i for i in hdr2] + ['Date difference (months)']
fid = open(out_file, 'w')
fid.write('\t'.join(hdr))
fid.write('\n')
for row in merged_data:
    str_row = [str(i) for i in row]
    fid.write('\t'.join(str_row))
    fid.write('\n')
fid.close()