# Converts the DTI sampling for TSA from the VTK format to R files
import re
import numpy as np
from rpy2.robjects import r
from rpy2.robjects.numpy2ri import numpy2ri


dir_name = '/mnt/shaw/dti_robust_tsa/analysis_99redo/'
# dir_name = '/Users/sudregp/tmp/dti/'
subj_file = 'subjs_diffeo.txt'
r_output_file = 'mean_sampling'
tract_names = ['left_cst', 'left_ifo', 'left_ilf', 'left_slf', 'left_unc', 'right_cst', 'right_ifo', 'right_ilf', 'right_slf', 'right_unc', 'cc']
var_names = ['FA', 'ADC', 'PD', 'AD', 'RD']#, 'eig1', 'eig2', 'eig3']

# find out the subject names so we can have nice names on the table rows
subj_names = []
fid = open(dir_name + subj_file, 'r')
for line in fid:
    subj_names.append(line.split('_')[0])
fid.close()
num_subjects = len(subj_names)

tract_var_names = []

# for each tract file, read all variables
for tract in tract_names:
    print 'opening', tract
    # .mean. or .maxFA.
    fid = open(dir_name + 'ixi_template_' + tract + '_def3.med.mean.vtk', 'r')
    data = fid.read()
    # get rid of new lines
    data = data.replace('\n', '')

    m_obj = re.search("POINTS (\d+) float", data)
    num_points = int(m_obj.group(1))

    for var in var_names:
        print "looking at variable", var
        # make sure the number of subjects matches the list of names
        m_obj = re.search(var + " (\d+) (\d+) float", data)
        thisSubjects = int(m_obj.group(1))
        if var == 'PD':
            # this is a special case because it's a vector field, so we have 3 points per subject
            goal_subjects = num_subjects * 3
        else:
            goal_subjects = num_subjects

        if thisSubjects != goal_subjects:
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
                cnt += thisSubjects
                # add the data for this point to all the other points
                all_points.append(point_val)
            # create the labels for each subject column
            array = np.array(all_points, dtype="float64")
        # fout = open('/Users/sudregp/tmp/' + var + '_' + tract + '_maxFA_trans.csv', 'w')
        # wr = csv.writer(fout)
        # wr.writerows(array)
        # fout.close()
            tract_var_names.append(var + '_' + tract)
            ro = numpy2ri(array)
            r.assign(tract_var_names[-1], ro)
    fid.close()
r("save(" + ','.join(tract_var_names) + ", file='" + r_output_file + ".gzip', compress=TRUE)")
