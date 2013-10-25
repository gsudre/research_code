# Script for Eszter to replace IDs
import numpy as np
import os
import glob
import matplotlib.mlab as mlab
import shutil


mapFile = '/Users/sudregp/eszter/Gustavo_wave 3/Wave_3_all_IDs_merged.csv'
dirRoot = '/Users/sudregp/eszter/Gustavo_wave 3/Network data wave 3/'

mymap = np.recfromcsv(mapFile)
# for each row in the map file
for r, rec in enumerate(mymap):
    print 'Row', r+1, '/', len(mymap)
    # figure out the files to open based on school and class name
    dirName = dirRoot + rec[5] + '/per klas/' + rec[6] + '/'
    if not os.path.exists(dirName):
        print 'Directory', dirName, 'not found.'
    else:
        testFiles = glob.glob(dirName + '*.csv')
        # for each file, if there's no modified version of it, create it
        for fname in testFiles:
            if fname.find('modified') < 0:
                modName = fname[:-4] + '_modified.csv'
                if not os.path.exists(modName):
                    shutil.copyfile(fname, modName)
        # for each file in the directory, replace all the occurrences of the first column by the 3rd column
        for fname in testFiles:
            # only operate on modified files
            if fname.find('modified') >= 0:
                data = np.recfromcsv(fname)
                changed = False
                # look for occurrences in the first column
                for row in data:
                    if row[0]==rec[0]:
                        row[0] = rec[2]
                        changed = True
                # look for occurrences in the first row. The header is read in as a
                # tuple, so we need to do it differently
                new_names = []
                for column in data.dtype.names:
                    if column==str(rec[0]):
                        new_names.append(str(rec[2]))
                    else:
                        new_names.append(column)
                data.dtype.names = new_names
                if changed:
                    mlab.rec2csv(data, fname)
