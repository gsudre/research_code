'''

Given a temporary folder and a destination folder, organizes the files downloaded from the DICOM server using the mask IDS queried from LabMatrix.

Note that this script assumes the data has been collected properly. In the cases when the study is incomplete, and there are more than one scan session per maskID, upload the incomplete files manually to the directory structure!

It also creates a CSV file to be uploaded to Labmatrix to populate Scan fields.

Gustavo Sudre, 10/2013

'''

import os
import glob
import tarfile
import shutil
import re
import pdb

# File summarizing the scaning day(s)
email = '/Users/sudregp/tmp/email.txt'
# Where to output the scan records
csvOutput = '/Users/sudregp/tmp/scans2.csv'
# where to find .tar.gz with downloaded MR data
tmpFolder = '/Users/sudregp/Downloads/'
# target folder to upack the data
mrFolder = '/Volumes/neuro/MR_data/'
# where to place symbolic links
symlinkFolder = '/Volumes/neuro/data_by_maskID/'

# type of modalities we scan
# note that these names need to be found in the README file!
modInReadme = ['rage', 'fmri', 'rest', 'edti', 'clinical', 'fat_sat']  
# how they should be called in the Scan record (same order!)
modInCSV = ['MPRAGE', 'stop task', 'rest', 'eDTI', 'clinical', 'T2']


# Function that checks whether we scanned a certain type of data (dtype) in a given data folder
def check_for_data(dtype, folder):
    dataFolder = glob.glob(folder + '/20*')
    # get the name of the text file
    txtfile = glob.glob(dataFolder[0] + '/README*.txt')
    fid = open(txtfile[0])
    text = fid.read()
    pos = text.lower().find(dtype)
    if pos > 0:
        return 1

    # if we get to here, we didn't find the type fo data in any of the matching folders
    return -1


# parse the e-mail Dan sends
# MAKE SURE THERE ARE ONLY SUBJECTS WITH NEUROIMAGES IN THE EMAIL!
fid = open(email, 'r')
names = {}
scores = {}
ages = {}
taskIDs = {}
subjectNames = None
subjectAge = None
subjectScore = None
subjectTaskId = None
for line in fid:
    # check if it's a mask id
    match = re.search("mask id: ncr(\S+)", line.lower())
    if match is not None:
        maskid = int(match.group(1))

    # check if it's a task
    match = re.search("task id: (\S+)", line.lower())
    if match is not None:
        subjectTaskId = match.group(1)
    
    # check if it's a MPRAGE score
    match = re.search("mprage score: (\S+)", line.lower())
    if match is not None:
        subjectScore = match.group(1)

    # check if it's the subject's info
    match = re.search("([\w ]*) \((.*)\)", line)
    if match is not None:
        subjectNames = match.group(1).split(' ')
        subjectAge = 'young'
        for word in match.group(2).split(' '):
            if word == 'adult':
                subjectAge = 'adult'

    # just finished a subject
    if line == '\n':
        names[maskid] = subjectNames
        scores[maskid] = subjectScore
        ages[maskid] = subjectAge
        taskIDs[maskid] = subjectTaskId
        subjectNames = None
        subjectAge = None
        subjectScore = None
        subjectTaskId
fid.close()

# make sure we add the last subject, in case the file didn't end with a new line
if line != '\n':
    names[maskid] = subjectNames
    scores[maskid] = subjectScore
    ages[maskid] = subjectAge
    taskIDs[maskid] = subjectTaskId

# match the DICOMs we find in the folder to their info from the e-mail
dicoms = glob.glob(tmpFolder + '/*-DICOM*')
file2maskid = []
print 'Found these DICOM files in ' + tmpFolder + ':\n'
for file in dicoms:
    found = False
    print file
    subjectName = file.split('-')[0].split('/')[-1]
    # find the mask id sent in the email
    for key, val in names.iteritems():
        # here we assume names only stores first and last name!
        if (subjectName.find(val[0].upper()) >= 0 and
           subjectName.find(val[1].upper()) >= 0):
            file2maskid.append(key)
            print 'Mask ID:', key
            found = True
    if not found:
        print 'ERROR: Could not find mask ID in e-mail!'

raw_input('\nPress any key to start sorting, or Ctrl+C to quit...')

# lists to store info for CSV
subjectMRNs = []
datesCollected = []
scanTypes = []
scanners = []
maskIDs = []
taskIDsCSV = []
mprageQuality = []

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
        elif len(ecgData) == 1 and ages[curMaskId]=='adult':
            print '\tOnly found one set of physiological data!'
        # adults should have 4 + 1 physiological files
        elif len(ecgData) != 5 and ages[curMaskId]=='adult':  
            print '\tFound unexpected number of physiological files (%d)!' % len(ecgData)

    # moving extracted files inside maskId folder
    folder2move = glob.glob(targetFolder + '/*' + mrn + '/*')
    shutil.move(folder2move[0], targetFolder)
    os.rmdir(targetFolder + '/' + subjectName + '-' + mrn + '/')

    # create symlink in data_by_maskid folder
    print 'Creating symlinks...'
    linkName = symlinkFolder + ('%04.0d' % curMaskId)
    source = '../MR_data/' + folder2move[0].split('/')[-2] + '/' + str(curMaskId)
    if not os.path.exists(linkName):
        os.symlink(source, linkName)
    else:
        print 'WARNING: Link already exists!'    

    # get the information we'll need for the CSV file
    for midx, mod in enumerate(modInReadme):
        if check_for_data(mod, targetFolder):
            subjectMRNs.append(mrn) 
            maskIDs.append(curMaskId)
            datesCollected.append(file.split('-')[2])
            scanTypes.append(modInCSV[midx])
            scanners.append('3TA')
            if mod == 'fmri' and taskIDs[curMaskId] is not None:
                taskIDsCSV.append(taskIDs[curMaskId])
            else:
                taskIDsCSV.append('')
            if mod == 'rage' and scores[curMaskId] is not None:
                mprageQuality.append(scores[curMaskId])
            else:
                mprageQuality.append('')

headers = 'MRN,Date,Type,Scanner,Mask ID,MPRAGE quality,Task / MEG ID,Notes\n'
fid = open(csvOutput, 'w')
fid.write(headers)
for i in range(len(subjectMRNs)):
    fid.write(subjectMRNs[i] + ',' + datesCollected[i] + ',' + scanTypes[i]
              + ',' + scanners[i] + ',' + str(maskIDs[i]) + ','
              + mprageQuality[i] + ',' + taskIDsCSV[i] + '\n')
fid.close()

print 'Done storing files in server and outputting CSV.'
print 'REMEMBER: add any extra notes to the Notes column in', csvOutput