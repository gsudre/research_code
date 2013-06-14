import numpy as np
import math

filename = '/Volumes/PIETRO/1030.txt'

# Stores the offset of the period after getting the trigger from the scanner (i.e. the "Get Ready" window)
blockStartCol = 'GetRdy.FinishTime'

# Define variables set in the scanner
actualTRLength = 2000
numDummyTRs = 4

# Expected number of trial in each run
expectedTrialNum = 86

# Stores the TR duration that was entered during the scan.
trLengthCol = 'VDurn'

# Stores trial types (i.e. STI, STG, STB)
trialTypeCol = 'Procedure[Trial]'

# Stores the block number
trialBlockCol = 'Block'

# Stores boolean accuracy and reaction time in Go trials
stgCorrectCol = 'Go.ACC'
stgRTCol = 'Go.RT'

# Stores bpossible Inhibit trial responses and inhibition time
stiResponseCol = ['Go1s.RESP', 'Go2s.RESP', 'Inhs.RESP']
stiInhCol = 'GoDur'

#### STARTING SCRIPT ####

# Open data
data = np.recfromtxt(filename, delimiter='\t')

# Computes the delay (in ms) to augment the trial onset. If the time entered at the beginning of the task is the same as the length of the TR (e.g. 2000), then blockStartCol should happen 4 times the time entered according to the E-prime script. Since we have 4 dummy TRs, and assuming we crop out the first 4 TRs in fMRI preprocessing, then this delay equals to 0. However, we've been conservative and have been using 2300 in the begining, even though our TR is 2000. That means that when we crop the fMRI data after the first 4 TRs (8000 ms), our task only actually began at 4 * 2300 = 9200. The delay below corresponds to that difference.
idjEnteredTR = np.nonzero(data[0, :] == trLengthCol)[0]
enteredTRLength = int(data[2, idjEnteredTR][0])
delay = numDummyTRs * (enteredTRLength - actualTRLength)

# Figure out how many blocks we have, based on the variable that stores the offset of the waiting period
idjBlockStart = np.nonzero(data[0, :] == blockStartCol)[0]
# we add one because the matrix we loop through removes the headers
blockStartRows = [i + 1 for i, s in enumerate(data[1:, idjBlockStart]) if len(s[0]) > 1]
if len(blockStartRows) != 4:
    err = 'Found ' + str(len(blockStartRows)) + ' blocks'
    raise NameError(err)

# Make sure we have all the trials we are expecting
idjBlockNum = np.nonzero(data[0, :] == trialBlockCol)[0]
rowsPerBlock = []
for blockIdx, blockRow in enumerate(blockStartRows):
    # Get the number of the block and all the rows that correspond to that block. They start on the row right after where the block started
    blockNum = data[blockRow + 1, idjBlockNum]
    blockTrials = [i for i, s in enumerate(data[:, idjBlockNum]) if s[0] == blockNum]
    if len(blockTrials) != expectedTrialNum:
        err = 'Found ' + str(len(blockTrials)) + 'trials in block ' + str(blockIdx + 1)
        raise NameError(err)
    else:
        rowsPerBlock.append(blockTrials)

# Calculating the behavioral variables per block
idjTrialType = np.nonzero(data[0, :] == trialTypeCol)[0]
idjGoAcc = np.nonzero(data[0, :] == stgCorrectCol)[0]
idjRTAcc = np.nonzero(data[0, :] == stgRTCol)[0]
idjStiResp = [np.nonzero(data[0, :] == s)[0] for s in stiResponseCol]
idjStiDur = np.nonzero(data[0, :] == stiInhCol)[0]
stgAcc = []
stgMeanRT = []
stgStdRT = []
stgRT = []
stiAcc = []
stiMeanDur = []
stiStdDur = []
stiDur = []
for trials in rowsPerBlock:
    # identify go trials. Note that the indices refer to the variable trials, and NOT to the direct data matrix indexes!
    correctGoTrials = [trials[i] for i, s in enumerate(data[trials, idjTrialType]) if s == 'StGTrial' and data[trials[i], idjGoAcc] == '1']
    incorrectGoTrials = [trials[i] for i, s in enumerate(data[trials, idjTrialType]) if s == 'StGTrial' and data[trials[i], idjGoAcc] == '0']

    # compute percent accuracy. Again, here the indices correspond to GoTrials!
    stgAcc.append(100 * float(len(correctGoTrials)) / (len(correctGoTrials) + len(incorrectGoTrials)))

    # compute mean and std RT over the accurate trials
    stgBlockRTs = [int(i) for i in data[correctGoTrials, idjRTAcc]]
    stgMeanRT.append(np.mean(stgBlockRTs))
    stgStdRT.append(np.std(stgBlockRTs))

    # identify inhibit trials
    incorrectInhTrials = []
    correctInhTrials = []
    for i, s in enumerate(data[trials, idjTrialType]):
        if s == 'StITrial':
            if data[trials[i], idjStiResp[0]] == '' and data[trials[i], idjStiResp[1]] == '' and data[trials[i], idjStiResp[2]] == '':
                correctInhTrials.append(trials[i])
            else:
                incorrectInhTrials.append(trials[i])

    # compute percent accuracy
    stiAcc.append(100 * float(len(correctInhTrials)) / (len(correctInhTrials) + len(incorrectInhTrials)))

    # compute mean and std inhitbit delay over accurate trials
    stiBlockDur = [int(i) for i in data[correctInhTrials, idjStiDur]]
    stiMeanDur.append(np.mean(stiBlockDur))
    stiStdDur.append(np.std(stiBlockDur))

    # concatenate Go RTs for correct trials so we can later interpolate SSRT. Let's concatenate duration as well so we can have a better std later
    stgRT.append(stgBlockRTs)
    stiDur.append(stiBlockDur)

# Now we interpolate to get SSRT. First, order correctGoTrials based on RT, then choose the number relative to the STI accuracy

# just flattening the lists first
stgRT = np.sort([i for j in stgRT for i in j])
stiDur = np.sort([i for j in stiDur for i in j])

# Now we compile everything across blocks.
subjStgMeanRT = np.mean(stgRT)
subjStgStdRT = np.std(stgRT)
subjStiMeanDur = np.mean(stiDur)
subjStiStdDur = np.std(stiDur)
subjStgAcc = np.mean(stgAcc)
subjStiAcc = np.mean(stiAcc)

ll = int(math.floor(subjStiAcc / 100 * len(stgRT)))
ul = int(math.ceil(subjStiAcc / 100 * len(stgRT)))
subjXthPercentile = (stgRT[ul] + stgRT[ll]) / 2
subjSSRT = subjXthPercentile - subjStiMeanDur

print 'STG accuracy:', subjStgAcc
print 'STG RT:', subjStgMeanRT, '+-', subjStgStdRT
print 'STI accuracy:', subjStiAcc
print 'STI duration:', subjStiMeanDur, '+-', subjStiStdDur
print 'xth percentile STG RT:', subjXthPercentile
print 'Corrected SSRT:', subjSSRT
