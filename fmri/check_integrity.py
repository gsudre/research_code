# Checks the integrity of a behavioral file (i.e. are all blocks on the same day and in the correct order?)
import numpy as np
import sys
import glob

#### DEFINING VARIABLES AND COLUMN NAMES FROM E-PRIME EXPORTED FILE ####

# Stores the offset of the period after getting the trigger from the scanner (i.e. the "Get Ready" window)
blockStartCol = 'GetRdy.FinishTime'

sessionDateCol = 'SessionDate'


#### STARTING SCRIPT ####

# if there was one argument, run the script for the one file. Otherwise, run it for all subjects in the folder
if len(sys.argv) == 2:
    files = [sys.argv[1]]
elif len(sys.argv) == 1:
    files = glob.glob('*.txt')
else:
    raise('Wrong number of arguments to script!')

# files = ['/Volumes/neuro/MR_behavioral/exported_data/0214_m.txt']

for txtFile in files:
    subj = txtFile[:-4]
    print 'Analyzing file ' + subj
    # Open data
    data = np.recfromtxt(txtFile, delimiter='\t')

    # Figure out how many blocks we have, based on the variable that stores the offset of the waiting period
    idjBlockStart = np.nonzero(data[0, :] == blockStartCol)[0]
    # we add one because the matrix we loop through removes the headers
    blockStartRows = [i + 1 for i, s in enumerate(data[1:, idjBlockStart]) if len(s[0]) > 1]
    if len(blockStartRows) != 4:
        print 'WARNING: FOUND', len(blockStartRows), 'BLOCKS!!!'

    # check that they were all on the same day
    idjSessionDate = np.nonzero(data[0, :] == sessionDateCol)[0]
    if len(np.unique(data[blockStartRows, idjSessionDate])) > 1:
        print 'ERROR: More than one unique date in SessionDate column!'

    # check that the block start time is increasing
    blockStartTimes = data[blockStartRows, idjBlockStart]
    tmp = np.array([int(s) for s in blockStartTimes])
    # correct the timing for blocks > 4
    if len(tmp) > 4:
        tmp[4:] += tmp[3]
    if len(tmp) > 8:
        tmp[8:] += tmp[7]
    if len(tmp) > 12:
        tmp[12:] += tmp[11]
    startDiffs = np.diff(tmp)
    if any(startDiffs <= 0):
        print "Error: blocks start in weird order!", blockStartTimes, tmp

