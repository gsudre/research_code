'''

Creates a matrix to go into Labmatrix based on the MEG data.

Gustavo Sudre, 03/2014

'''

import glob
import datetime
import pdb

# Where to output the scan records
csv_output = '/Users/sudregp/tmp/meg_scans.csv'
# where to find MEG data
meg_dir = '/mnt/neuro/MEG_data/raw/'


# type of modalities we scan
# note that these names need to be found in the README file!
mod_readme = ['stop', 'rest']  
# how they should be called in the Scan record (same order!)
mod_CSV = ['stop task', 'rest']


# Function that checks whether we scanned a certain type of data (dtype) in a given data folder
def check_for_data(dtype, folder):
    dataFolder = glob.glob(folder + '/20*')
    # get the name of the text file
    txtfile = glob.glob(dataFolder[0] + '/README*.txt')
    fid = open(txtfile[0])
    text = fid.read()
    pos = text.lower().find(dtype)
    if pos > 0:
        return True

    # if we get to here, we didn't find the type fo data in any of the matching folders
    return False


# lists to store info for CSV
datesCollected = []
scanTypes = []
scanners = []
maskIDs = []
taskIDsCSV = []
notes = []

date_dirs = glob.glob(meg_dir + '/*')
# for each date folder
for date_dir in date_dirs:
    my_date = datetime.datetime.strptime(date_dir.split('/')[-1], '%Y%m%d')
    my_date = datetime.datetime.strftime(my_date,'%m/%d/%Y')
    # find all subjects scanned on this date
    data_dirs = glob.glob(date_dir + '/*0?.ds')  # ignores -f.ds files
    subjs = [d.split('/')[-1].split('_')[0] for d in data_dirs]
    subjs = set(subjs)  # makes it unique
    for subj in subjs:
        for modr, modc in zip(mod_readme, mod_CSV):
            mod_data = glob.glob(date_dir + '/%s_%s_*0?.ds'%(subj, modr))
            if len(mod_data) > 1:
                mynote = '%d sessions'%len(mod_data)
            else:
                mynote = ''
            if mod_data:
                datesCollected.append(my_date)
                scanTypes.append(modc)
                scanners.append('MEG')
                maskIDs.append(subj)
                taskIDsCSV.append('')
                notes.append(mynote)

headers = 'Date,Type,Scanner,Mask ID,Task / MEG ID,Notes\n'
fid = open(csv_output, 'w')
fid.write(headers)
for i in range(len(datesCollected)):
    fid.write(datesCollected[i] + ',' + scanTypes[i]
              + ',' + scanners[i] + ',' + str(maskIDs[i]) + ','
              + taskIDsCSV[i] + ',' + notes[i] + '\n')
fid.close()