''' Puts a Y in every column in excel for which we have data in the server, and also creates the scan data sheet to be imported into labmatrix '''

import glob
import datetime as dt
import csv
import numpy as np


def check_for_data(dtype, folders):
    found = False
    for folder in folders:
        # now, get the name of the text file
        txtfile = glob.glob(folder + '/README*.txt')
        fid = open(txtfile[0])
        text = fid.read()
        pos = text.lower().find(dtype)
        found = found or (pos > 0)
    return found


path = '/Volumes/neuro/MR_data/'
max_date = dt.datetime.strptime('20130614', '%Y%m%d')  # last date we entered stuff in the spreadsheet. After that it went in Labmatrix

# open spreadsheet
fname = '/Volumes/Labs/Shaw/To Go Into LabMatrix/send_to_labmatrix/visit_records.txt'
csv_table_out = '/Users/sudregp/tmp/scan_table.csv'

# positions of these data in the sheet
vmrn = 0
vdate = 1
vclinical = 6
vmprage = 7
vtask = 8
vrest = 9
vedti = 10
vt2 = 11

list_mod = ['rage', 'fmri', 'rest', 'edti', 'clinical', 'fat_sat']  # note that these names need to be found in the README file!
scan_headers = ['MRN', 'Date', 'Type', 'Scanner', 'Mask ID', 'Task / MEG ID', 'MPRAGE Quality', 'Notes']
scan_table = []
scan_table.append(scan_headers)

visits = np.recfromtxt(fname, delimiter='\t')

# get a list of the subjects in the server
subjs = glob.glob(path + '/*')

errors = []
print "Add these rows to the visits spreadsheet:"

# for each subject in the server
for subj_dir in subjs:
    mrn = int(subj_dir.split('/')[-1].split('-')[-1])
    # look for all mask ids this subject has
    maskids = glob.glob(subj_dir + '/*')
    # for each mask id, figure out the date of scan so we can check the spreadsheet and create a new scan record
    for maskid_dir in maskids:
        mask_id = int(maskid_dir.split('/')[-1])
        # we could have more than one date directory inside the same mask ID when there were two scan sessions (e.g. the first one was interrupted). Still they'll share the same date!
        date_dirs = glob.glob(maskid_dir + '/20*')
        date = dt.datetime.strptime(date_dirs[0].split('/')[-1].split('-')[0].replace('_', ''), '%Y%m%d')

        if date < max_date:
            # looking for this particular entry in the spreadsheet
            vrow = [i for i in range(1, visits.shape[0])  # skipping headers
                    if mrn == int(visits[i][vmrn]) and
                    date == dt.datetime.strptime(visits[i][vdate], '%m/%d/%y')]

            # we'll need to output to the screen the new subjects to go into the visit record, so that we can merge it with the visit record later. Saving the excel file screws up the dates.
            new_visit = []
            if len(vrow) == 0:
                add_new = True
                new_visit.append(str(mrn))
                new_visit.append(str(date.strftime('%m/%d/%y')))
                for i in range(4):
                    new_visit.append('')
            else:
                add_new = False

            # check what kinds of data this subject has in this mask id. Create a new Scan table entry for each data type found
            if check_for_data('clinical', date_dirs):
                scan_table.append([mrn, date.strftime('%m/%d/%Y'), 'clinical', '3TA', mask_id, '', '', ''])
                new_visit.append('Y')
            else:
                new_visit.append('N')
            # # if it's not a new entry in visits spreasheet, but the value in the specific column for this modality is different than what we get by looking at the directory, give out an error
            if not add_new and visits[vrow[0]][vclinical] != new_visit[-1]:
                errors.append('%d on %s should be %c for clinical instead of %s' % (mrn, str(date.strftime('%m/%d/%y')), new_visit[-1], visits[vrow[0]][vclinical]))
                visits[vrow[0]][vclinical] = new_visit[-1]

            if check_for_data('rage', date_dirs):
                scan_table.append([mrn, date.strftime('%m/%d/%Y'), 'MPRAGE', '3TA', mask_id, '', '', ''])
                new_visit.append('Y')
            else:
                new_visit.append('N')
            if not add_new and visits[vrow[0]][vmprage] != new_visit[-1]:
                errors.append('%d on %s should be %c for MPRAGE instead of %s' % (mrn, str(date.strftime('%m/%d/%y')), new_visit[-1],  visits[vrow[0]][vmprage]))
                visits[vrow[0]][vmprage] = new_visit[-1]

            if check_for_data('fmri', date_dirs):
                scan_table.append([mrn, date.strftime('%m/%d/%Y'), 'stop task', '3TA', mask_id, '', '', ''])
                new_visit.append('Y')
            else:
                new_visit.append('N')
            if not add_new and visits[vrow[0]][vtask] != new_visit[-1]:
                errors.append('%d on %s should be %c for task instead of %s' % (mrn, str(date.strftime('%m/%d/%y')), new_visit[-1], visits[vrow[0]][vtask]))
                visits[vrow[0]][vtask] = new_visit[-1]

            if check_for_data('rest', date_dirs):
                scan_table.append([mrn, date.strftime('%m/%d/%Y'), 'rest', '3TA', mask_id, '', '', ''])
                new_visit.append('Y')
            else:
                new_visit.append('N')
            if not add_new and visits[vrow[0]][vrest] != new_visit[-1]:
                errors.append('%d on %s should be %c for rest instead of %s' % (mrn, str(date.strftime('%m/%d/%y')), new_visit[-1], visits[vrow[0]][vrest]))
                visits[vrow[0]][vrest] = new_visit[-1]

            if check_for_data('edti', date_dirs):
                scan_table.append([mrn, date.strftime('%m/%d/%Y'), 'eDTI', '3TA', mask_id, '', '', ''])
                new_visit.append('Y')
            else:
                new_visit.append('N')
            if not add_new and visits[vrow[0]][vedti] != new_visit[-1]:
                errors.append('%d on %s should be %c for eDTI instead of %s' % (mrn, str(date.strftime('%m/%d/%y')), new_visit[-1], visits[vrow[0]][vedti]))
                visits[vrow[0]][vedti] = new_visit[-1]

            if check_for_data('fat_sat', date_dirs):
                scan_table.append([mrn, date.strftime('%m/%d/%Y'), 'T2', '3TA', mask_id, '', '', ''])
                new_visit.append('Y')
            else:
                new_visit.append('N')
            if not add_new and visits[vrow[0]][vt2] != new_visit[-1]:
                errors.append('%d on %s should be %c for T2 instead of %s' % (mrn, str(date.strftime('%m/%d/%y')), new_visit[-1], visits[vrow[0]][vt2]))
                visits[vrow[0]][vt2] = new_visit[-1]

            if add_new:
                print "\t".join(new_visit)

fid = open(csv_table_out, 'w')
wr = csv.writer(fid)
wr.writerows(scan_table)
fid.close()

print '\nThese assignments are incorrect in the Excel matrix:'
for er in errors:
    print er

np.savetxt(fname[:-4] + '_corrected.txt', visits, fmt='%s', delimiter='\t')
