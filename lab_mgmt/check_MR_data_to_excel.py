''' Puts a Y in every column in excel for which we have data in the server, and also creates the scan data sheet to be imported into labmatrix '''

import glob
from datetime import datetime
import csv


def check_for_data(dtype, folder):
    # now, get the name of the text file
    txtfile = glob.glob(folder + '/README*.txt')
    fid = open(txtfile[0])
    text = fid.read()
    pos = text.lower().find(dtype)
    return (pos > 0)


path = '/Volumes/neuro/MR_data/'
max_date = datetime.strptime('20130614', '%Y%m%d')  # last date we entered stuff in the spreadsheet. After that it went in Labmatrix

# open spreadsheet
fname = r'/Users/sudregp/tmp/visit_records.xlsx'
csv_table_out = '/Users/sudregp/tmp/scan_table.csv'

list_mod = ['rage', 'fmri', 'rest', 'edti', 'clinical', 'fat_sat']  # note that these names need to be found in the README file!
scan_headers = ['MRN', 'Type', 'Scanner', 'Mask ID', 'Task / MEG ID', 'Notes', 'MPRAGE Quality']
scan_table = []
scan_table.append(scan_headers)

wb = load_workbook(filename=fname)
ws = wb.worksheets[0]

# get a list of the subjects in the server
subjs = glob.glob(path + '/*')

errors = []
print "Add these rows to the Excel spreadsheet:"

# for each subject in the server
for subj_dir in subjs:
    mrn = int(subj_dir.split('/')[-1].split('-')[-1])
    # look for all mask ids this subject has
    maskids = glob.glob(subj_dir + '/*')
    # for each mask id, figure out the date of scan so we can check the spreadsheet and create a new scan record
    for maskid_dir in maskids:
        mask_id = int(maskid_dir.split('/')[-1])
        date_dir = glob.glob(maskid_dir + '/2*')[0]
        date = datetime.strptime(date_dir.split('/')[-1].split('-')[0].replace('_', ''), '%Y%m%d')

        if date < max_date:
            # looking for this particular entry in the spreadsheet
            row_idx = [i for i in range(1, ws.get_highest_row()) if (mrn == ws.cell('A' + str(i)).value) and (date == ws.cell('B' + str(i)).value)]

            # we'll need to output to the screen the new subjects to go into the visit record, so that we can merge it with the visit record later. Saving the excel file screws up the dates.
            new_visit = []
            if len(row_idx) == 0:
                add_new = True
                new_visit.append(str(mrn))
                new_visit.append(str(date.strftime('%m/%d/%y')))
                for i in range(4):
                    new_visit.append('')
            else:
                add_new = False

            # check what kinds of data this subject has in this mask id. Create a new Scan table entry for each data type found
            if check_for_data('clinical', date_dir):
                scan_table.append([mrn, 'clinical', '3TA', mask_id, '', '', ''])
                new_visit.append('Y')
            else:
                new_visit.append('N')
            # if not add_new and ws.cell('G' + str(row_idx[0])).value != new_visit[-1]:
            #     errors.append('%d on %s should be %c' % (mrn, str(date.strftime('%m/%d/%y')), new_visit[-1]))

            if check_for_data('rage', date_dir):
                scan_table.append([mrn, 'MPRAGE', '3TA', mask_id, '', '', ''])
                new_visit.append('Y')
            else:
                new_visit.append('N')
            if not add_new and ws.cell('H' + str(row_idx[0])).value != new_visit[-1]:
                errors.append('%d on %s should be %c' % (mrn, str(date.strftime('%m/%d/%y')), new_visit[-1]))    

            if check_for_data('fmri', date_dir):
                scan_table.append([mrn, 'stop task', '3TA', mask_id, '', '', ''])
                new_visit.append('Y')
            else:
                new_visit.append('N')
            if not add_new and ws.cell('I' + str(row_idx[0])).value != new_visit[-1]:
                errors.append('%d on %s should be %c' % (mrn, str(date.strftime('%m/%d/%y')), new_visit[-1]))

            if check_for_data('rest', date_dir):
                scan_table.append([mrn, 'rest', '3TA', mask_id, '', '', ''])
                new_visit.append('Y')
            else:
                new_visit.append('N')
            if not add_new and ws.cell('J' + str(row_idx[0])).value != new_visit[-1]:
                errors.append('%d on %s should be %c' % (mrn, str(date.strftime('%m/%d/%y')), new_visit[-1]))

            if check_for_data('edti', date_dir):
                scan_table.append([mrn, 'eDTI', '3TA', mask_id, '', '', ''])
                new_visit.append('Y')
            else:
                new_visit.append('N')
            if not add_new and ws.cell('K' + str(row_idx[0])).value != new_visit[-1]:
                errors.append('%d on %s should be %c' % (mrn, str(date.strftime('%m/%d/%y')), new_visit[-1]))

            if check_for_data('fat_sat', date_dir):
                scan_table.append([mrn, 'T2', '3TA', mask_id, '', '', ''])
                new_visit.append('Y')
            else:
                new_visit.append('N')
            # if not add_new and ws.cell('L' + str(row_idx[0])).value != new_visit[-1]:
            #     errors.append('%d on %s should be %c' % (mrn, str(date.strftime('%m/%d/%y')), new_visit[-1]))

            if add_new:
                print "\t".join(new_visit)

fid = open(csv_table_out, 'w')
wr = csv.writer(fid)
wr.writerows(scan_table)
fid.close()

print '\nThese assignments are incorrect in the Excel matrix:'
print errors

# NEED TO WRITE THE CORRECTED STUFF TO A FILE INSTEAD OF TO SCREEN TO BE LATER MERGED TO EXCEL. OR JUST RE-WRITE A NEW TAB FILE. JUST DON'T REWRITE THE EXCEL BECAUSE IT SCREWS UP THE DATES
