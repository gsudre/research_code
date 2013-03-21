''' Script to check which subjects are lacking physiological data '''
import glob
import os

mr_folder = '/Volumes/neuro/MR_data/'

need_phys = []  # subjects that need physiological data
expected_rts = []  # scans for which we don't have RT folders
subjs = glob.glob(mr_folder + '/*')
for subj in subjs:
    # if it's a directory, check the maskIds inside it
    if os.path.isdir(subj):
        mask_ids = glob.glob(subj + '/*')
        # in each mask id, investigate all scans
        for mask in mask_ids:
            dicom_folders = glob.glob(mask + '/*-*')
            # here we have the fair assumption that there's only one dicom folder per mask ID
            scans = glob.glob(dicom_folders[0] + '/*')
            # if it's a rest or task scan, increase the number of physiological datasets we'll be looking for
            phys_num = 0
            for scan in scans:
                # have to skip the readme as well
                if os.path.isdir(scan):
                    dicoms = glob.glob(scan + '/*')
                    # the second file is always a data file, while the first one might be README
                    if dicoms[1].find('rest')>=0 or dicoms[1].find('audition')>=0:
                        phys_num += 1

            # now we know how many physiological files to expect. Go into the RT folder and check how many we actually have. The assumption again is that the first folder we find is the correct one. Also, only perform this check if we are indeed expecting physio files.
            if phys_num > 0:
                rt_folders = glob.glob(mask + '/E*')
                if len(rt_folders) == 0:
                    print 'Did not find real-time data for ' + subj
                    print '\tExpected ' + str(phys_num) + ' physiological file(s).'
                    need_phys.append(subj)
                    bar = dicom_folders[0].split('/')
                    scanId = bar[-1].split('-')
                    # Remove leading zeros from scanID
                    scanId = str(int(scanId[-1]))
                    expected_rts.append('E' + scanId)
                else:
                    # again, we assume that there is only one RT folder
                    ecgData = glob.glob(rt_folders[0] + '/ECG_*')
                    respData = glob.glob(rt_folders[0] + '/Resp_*')
                    if len(ecgData) != len(respData):
                        print 'Different numbers of respiration and ECG data for ' + subj
                        need_phys.append(subj)
                    elif len(ecgData) < phys_num:
                        print 'Did not find all physiological data for ' + subj
                        need_phys.append(subj)
                        print '\tExpected: ' + str(phys_num) + '. Found: ' + str(len(ecgData))
