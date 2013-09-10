# Converts CSV files with DTI results to VTK format
import os
import numpy as np
import re

tract_file = '/Volumes/neuro/registration_to_tsa/ixi_template_right_cst_def3.med.mean.vtk'
results_file = '/Users/sudregp/tmp/FA_right_cst_RESULTS.csv'

# find the correct file for the tract, copy it and append the columns in correct order to the new file
target_file = results_file[:-4] + '.vtk'
if not os.path.exists(tract_file):
    print 'Error: could not find tract file', tract_file
else:
    in_data = np.recfromcsv(results_file)
    # we don't need to store the voxel number
    out_data = np.empty([len(in_data), len(in_data[0]) - 1])
    for row in in_data:
        out_data[row[0]-1, :] = list(row)[1:]

    columns = in_data.dtype.names[1:]  # skip vertex number

    # we need to go line by line in the tract file to find where to modify the number of total variables
    fin = open(tract_file, 'r')
    fout = open(target_file, 'w')
    for line in fin:
        m_obj = re.search("FIELD FieldData (\d+)\n", line)
        # update number of variables when we find it
        if m_obj is not None:
            num_vars = int(m_obj.groups()[0])
            num_vars += len(columns)
            new_line = "FIELD FieldData %d\n"%num_vars
            fout.write(new_line)
        else:
            fout.write(line)

    # out_data has the values for all voxels in order. We need to write each column with their correct name to the text file
    for c, col in enumerate(columns):
        fout.write('\n\n%s 1 %d float\n'%(col, out_data.shape[0]))
        out_data[:, c].tofile(fout, sep=" ", format="%.4f")

    fid.close()
    fout.close()

#STILL NEED TO HANDLE SPECIAL CASE OF VECTORS!