''' Script to check which subjects are lacking physiological data '''
import glob
import os


def check_1Ds(scans):
    # checking if we have 1D physiological data
    missing = 0
    for scan in scans:
        bar = scan.split('/')
        sep = '/'
        path = sep + sep.join(bar[1:-1]) + '/'
        bar = bar[-1].split('-')
        scan_num = bar[-1]
        # we have already checked that the number of EKG and respiration files are the same!
        physData = glob.glob(path + '/Resp_*' + scan_num + '.1D')
        if len(physData) < 1:
            missing += 1
    return missing


mr_folder = '/Volumes/neuro/MR_data/'

need_phys = []  # subjects that need physiological data
expected_rts = []  # scans for which we don't have RT folders
subjs = glob.glob(mr_folder + '/*')
for subj in subjs:
    subj_name = subj.split()[-1]
    # if it's a directory, check the maskIds inside it
    if os.path.isdir(subj):
        mask_ids = glob.glob(subj + '/*')
        # in each mask id, investigate all scans
        for mask in mask_ids:
            dicom_folders = glob.glob(mask + '/*-*')
            # here we have the fair assumption that there's only one dicom folder per mask ID
            scans = glob.glob(dicom_folders[0] + '/*')
            # if it's a rest or task scan, increase the number of physiological datasets we'll be looking for
            rest_num = 0
            task_num = 0
            for scan in scans:
                # have to skip the readme as well
                if os.path.isdir(scan):
                    dicoms = glob.glob(scan + '/*')
                    # the second file is always a data file, while the first one might be README
                    if dicoms[1].find('rest') >= 0:
                        rest_num += 1
                    elif dicoms[1].find('audition') >= 0:
                        task_num += 1

            # now we know how many physiological files to expect. Go into the RT folder and check how many we actually have. The assumption again is that the first folder we find is the correct one. Also, only perform this check if we are indeed expecting physio files.
            # pdb.set_trace()
            if (task_num + rest_num) > 0:
                rt_folders = glob.glob(mask + '/E*')
                if len(rt_folders) == 0:
                    print 'Did not find real-time data for ' + subj
                    print '\tExpected ' + str(rest_num + task_num) + ' physiological file(s).'
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
                    else:
                        # now we open each text file and check which ones are rest and which ones are task
                        scan_descriptors = glob.glob(rt_folders[0] + '/scan_*')
                        rest_scans = []
                        task_scans = []
                        for scan in scan_descriptors:
                            fid = open(scan)
                            text = fid.read()
                            series_start = int(text.find('Series De')) + 10
                            if text[series_start:series_start+4] == 'Audi':
                                task_scans.append(scan)
                            elif text[series_start:series_start+4] == 'rest':
                                rest_scans.append(scan)

                        # the number of text files and DICOM folders need to match, otherwise there is something word
                        if rest_num != len(rest_scans):
                            print 'Error in subject ' + subj
                            print '\tFound ' + str(rest_num) + ' resting DICOMS but ' + str(len(rest_scans)) + ' scan text files!'
                            need_phys.append(subj)
                        elif task_num != len(task_scans):
                            print 'Error in subject ' + subj
                            print '\tFound ' + str(task_num) + ' task DICOMS but ' + str(len(task_scans)) + ' scan text files!'
                            need_phys.append(subj)
                        else:
                            # everything matches, so let's check the actual physiological data
                            missing_rest = check_1Ds(rest_scans)
                            missing_task = check_1Ds(task_scans)
                            if missing_rest + missing_task > 0:
                                print 'Error in subject ' + subj_name
                                if missing_rest > 0:
                                    print '\tDid not find enough rest physiological data. ' + str(missing_rest) + '/' + str(rest_num) + ' files missing.'
                                if missing_task > 0:
                                    print '\tDid not find enough task physiological data. ' + str(missing_task) + '/' + str(task_num) + ' files missing.'
