import re
import numpy as np
import csv

dir_name = '/Volumes/neuro/registration_to_tsa/'
subj_file = 'subjs_diffeo.txt'
tract_names = ['left_cst', 'left_ifo', 'left_ilf', 'left_slf', 'left_unc', 'right_cst', 'right_ifo', 'right_ilf', 'right_slf', 'right_unc', 'cc']
var_names = ['FA', 'ADC', 'PD', 'AD', 'RD']

# find out the subject names so we can have nice names on the table rows
subj_names = []
fid = open(dir_name + subj_file, 'r')
for line in fid:
    subj_names.append(line.split('_')[0])
fid.close()
num_subjects = len(subj_names)

# for each tract file, read all variables
for tract in tract_names:
    print 'opening', tract
    fid = open(dir_name + 'ixi_template_' + tract + '_def3.med.mean.vtk','r')
    data = fid.read()
    # get rid of new lines
    data = data.replace('\n', '')

    m_obj = re.search("POINTS (\d+) float", data)
    num_points = int(m_obj.group(1))

    for var in var_names:
        print "looking at variable", var
        # make sure the number of subjects matches the list of names
        m_obj = re.search(var + " (\d+) (\d+) float", data)
        if var == 'PD':
            # this is a special case because it's a vector field, so we have 3 points per subject
            thisSubjects = int(m_obj.group(1))
            if thisSubjects != num_subjects*3:
                print "Different number of subjects in " + var
            else:
                # figure out where the index of the first number starts
                start_pos = m_obj.end()
                # split everything, even though we are only going to look up until however many numbers we need (it's a cheap operation)
                numbers = data[start_pos:].split(' ')
                cnt = 0
                all_points = []
                for p in range(num_points):
                    # convert all the values for each subject in this point 
                    point_val = [float(num) for num in numbers[cnt:cnt+thisSubjects]]
                    # attach the point name to later be a header
                    point_val = ['p' + str(p + 1)] + point_val
                    cnt += thisSubjects
                    # add the data for this point to all the other points
                    all_points.append(point_val)
                # create x,y,z labels for each subject    
                subj_points = [subj + '_' + vector for subj in subj_names for vector in ['x','y','z']] 
                # create the labels for each subject row
                array = np.array([['subjs'] + subj_points] + all_points).T
        else:
            thisSubjects = int(m_obj.group(1))
            if thisSubjects != num_subjects:
                print "Different number of subjects in " + var
            else:
                # figure out where the index of the first number starts
                start_pos = m_obj.end()
                numbers = data[start_pos:].split(' ')
                cnt = 0
                all_points = []
                for p in range(num_points):
                    point_val = [float(num) for num in numbers[cnt:cnt+num_subjects]]
                    point_val = ['p' + str(p + 1)] + point_val
                    cnt += num_subjects
                    all_points.append(point_val)
                array = np.array([['subjs'] + subj_names] + all_points).T
        fout = open('/Users/sudregp/tmp/' + var + '_' + tract + '.csv', 'w')
        wr = csv.writer(fout)
        wr.writerows(array)
        fout.close()
    fid.close()
