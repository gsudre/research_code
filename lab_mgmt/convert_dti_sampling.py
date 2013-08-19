import re
import numpy as np
import csv

dir_name = '/Volumes/neuro/registration_to_tsa/'
subj_file = 'subjs_diffeo.txt'
tract_names = ['cc', 'left_cst', 'left_ifo', 'left_ilf', 'left_slf', 'left_unc', 'right_cst', 'right_ifo', 'right_ilf', 'right_slf', 'right_unc']
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
                start_pos = m_obj.end() + 1
                cnt = 0
                # this will hold a list of lists
                all_points = []
                for p in range(num_points):
                    # we have one list per point. it starts with the point name, and then there is one point per subject.
                    point_val = ['p' + str(p + 1)]
                    for s in range(thisSubjects):
                        point_val.append(float(data[start_pos:].split(' ')[cnt]))
                        cnt = cnt + 1
                    # appending all subject data for this particular point
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
                start_pos = m_obj.end() + 1
                cnt = 0
                all_points = []
                for p in range(num_points):
                    point_val = ['p' + str(p + 1)]
                    for s in range(num_subjects):
                        point_val.append(float(data[start_pos:].split(' ')[cnt]))
                        cnt = cnt + 1
                    all_points.append(point_val)
                array = np.array([['subjs'] + subj_names] + all_points).T
        fout = open('/Users/sudregp/tmp/' + var + '_' + tract + '.csv', 'w')
        wr = csv.writer(fout)
        wr.writerows(array)
        fout.close()
    fid.close()
