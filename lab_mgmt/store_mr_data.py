'''

Given a temporary folder and a destination folder, organizes the files
downloaded from the DICOM server using the mask IDS queried from LabMatrix.

Note that this script assumes the data has been collected properly. In the
cases when the study is incomplete, and there are more than one scan session
per maskID, upload the incomplete files manually to the directory structure!

It also creates a CSV file to be uploaded to Labmatrix to populate Scan fields.

Gustavo Sudre, 10/2013

'''

import os
import glob
import tarfile
import shutil
import numpy as np
import datetime
import sys


# Where to output the scan records
csvOutput = '/Users/sudregp/tmp/scans.csv'
# where to find .tar.gz with downloaded MR data
tmpFolder = '/Users/sudregp/Downloads/'
# target folder to upack the data
mrFolder = '%s/MR_data/' % sys.argv[1]
# where to place symbolic links
symlinkFolder = '%s/data_by_maskID/' % sys.argv[1]

# type of modalities we scan
# note that these names need to be found in the README file!
# used to look for fmri for stop task, but not running it anymore!
modInReadme = ['rage_', 'ZZZZZZZ', 'rest', 'edti', 'clinical', 'fat_sat']
# how they should be called in the Scan record (same order!)
modInCSV = ['MPRAGE', 'stop task', 'rest', 'eDTI', 'clinical', 'T2']


# Function that checks whether we scanned a certain type of data (dtype) in a
# given data folder
def check_for_data(dtype, folder):
    dataFolder = glob.glob(folder + '/20*')
    # get the name of the text file
    txtfile = glob.glob(dataFolder[0] + '/README*.txt')
    fid = open(txtfile[0])
    text = fid.read()
    pos = text.lower().find(dtype)
    if pos > 0:
        return True

    # if we get to here, we didn't find the type fo data in any of the matching
    # folders
    return False


# find out what's the next mask id to use
maskid_dirs = glob.glob(symlinkFolder + '????')
curMaskId = [int(m.split('/')[-1]) for m in maskid_dirs]
curMaskId = max(curMaskId) + 1

# assign a mask ID for each DICOM we find
dicoms = glob.glob(tmpFolder + '/*-DICOM*')
file2maskid = []
print 'Found these DICOM files in ' + tmpFolder + ':\n'
for file in dicoms:
    print file
    file2maskid.append(curMaskId)
    print 'Mask ID:', curMaskId
    curMaskId += 1

raw_input('\nPress any key to start sorting, or Ctrl+C to quit...')

# lists to store info for CSV
subjectNames = []
subjectMRNs = []
datesCollected = []
scanTypes = []
scanners = []
maskIDs = []
notes = []

# while we still have subjects to uncompress
for fidx, file in enumerate(dicoms):
    # strip out the components of the filename
    bar = file.split('-')
    subjectName = bar[0].split('/')
    subjectName = subjectName[-1]
    mrn = bar[1]
    scanId = bar[3]

    curMaskId = file2maskid[fidx]

    subjFolder = mrFolder + '/' + subjectName + '-' + mrn + '/'
    targetFolder = subjFolder + '/' + str(curMaskId)

    # if we already have the MRN in our tree, that's our target directory
    dir = os.path.dirname(targetFolder)
    # create directory if not exist
    if not os.path.exists(dir):
        os.makedirs(dir)

    # Unpack the DICOMs to the tree
    print 'Unpacking ' + file
    tar = tarfile.open(file)
    tar.extractall(targetFolder)
    tar.close()

    # Remove leading zeros from scanID
    scanId = str(int(scanId))

    rtData = glob.glob(tmpFolder + '/E' + scanId + '.*')
    if len(rtData) == 0:
        print 'WARNING: Could not find real-time data!'
        rtCopied = 'N'
    else:
        print 'Unpacking ' + rtData[0]
        tar = tarfile.open(rtData[0])
        tar.extractall(targetFolder)
        tar.close()
        rtCopied = 'Y'

        # checking if we have all the physiological data we need
        ecgData = glob.glob(targetFolder + '/E' + scanId + '/ECG_*')
        respData = glob.glob(targetFolder + '/E' + scanId + '/Resp_*')
        if len(ecgData) != len(respData):
            print '\tDifferent numbers of respiration and ECG data!'
        elif len(ecgData) == 1:
            print '\tOnly found one set of physiological data!'
        # adults should have 4 + 1 physiological files
        elif len(ecgData) != 5:
            print '\tFound unexpected number of physiological files ' +\
                  '(%d)!' % len(ecgData)

    # moving extracted files inside maskId folder
    folder2move = glob.glob(targetFolder + '/*' + mrn + '/*')
    shutil.move(folder2move[0], targetFolder)
    os.rmdir(targetFolder + '/' + subjectName + '-' + mrn + '/')

    # get the information we'll need for the CSV file
    for midx, mod in enumerate(modInReadme):
        if check_for_data(mod, targetFolder):
            subjectNames.append(subjectName)
            subjectMRNs.append(mrn)
            maskIDs.append(curMaskId)
            myDate = file.split('-')[2]
            myDate = datetime.datetime.strptime(myDate, '%Y%m%d')
            datesCollected.append(datetime.datetime.strftime(myDate,
                                                             '%m/%d/%Y'))
            scanTypes.append(modInCSV[midx])
            scanners.append('3TA')
            if mod == 'edti':
                # checking the duration of cdi99 if any
                edti99_file = targetFolder + '/E' + scanId + '/cdiflist99'
                if os.path.exists(edti99_file):
                    e99 = np.genfromtxt(edti99_file, skip_header=1)
                    nslices = e99.shape[0]
                    e99Duration = nslices * 18.696
                    notes.append('edti99 duration: %.2f sec.' % e99Duration)
                else:
                    notes.append('No edti99 used.')
            else:
                notes.append('')


headers = 'Name,MRN,Date,Type,Scanner,Mask ID,Task / MEG ID,Notes,' +\
          'MPRAGE quality\n'
fid = open(csvOutput, 'w')
fid.write(headers)
for i in range(len(subjectMRNs)):
    fid.write(subjectNames[i] + ',' + subjectMRNs[i] + ',' +
              datesCollected[i] + ',' + scanTypes[i] + ',' + scanners[i] +
              ',' + str(maskIDs[i]) + ',' + '' + ',' + notes[i] + ',' + '' +
              '\n')
fid.close()

print 'Done storing files in server and outputting CSV.'
print 'REMEMBER: add any extra notes to the Notes column in', csvOutput
