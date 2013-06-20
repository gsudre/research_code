import numpy as np
import math
import sys
import glob

#### DEFINING VARIABLES AND COLUMN NAMES FROM E-PRIME EXPORTED FILE ####

# QC criteria for STG accuracy (in pct)
qcSTGAcc = 55

# CSV file to export behavioral scores
csv_filename = 'summary_behavioral_scores.csv'

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

# Stores possible Inhibit trial responses and inhibition time
stiResponseCol = ['Go1s.RESP', 'Go2s.RESP', 'Inhs.RESP']
stiInhCol = 'GoDur'

# Stores the onset time of each condition and their names
condNames = ['STG-correct', 'STG-incorrect', 'STI-correct', 'STI-incorrect', 'STB']
condOnsetCol = ['Go.OnsetTime', 'Go.OnsetTime', 'Go1s.OnsetTime', 'Go1s.OnsetTime', 'Go.OnsetTime']

#### STARTING SCRIPT ####

# if there was one argument, run the script for the one file. Otherwise, run it for all subjects in the folder
if len(sys.argv) == 2:
    files = [sys.argv[1]]
elif len(sys.argv) == 1:
    files = glob.glob('????.txt')
else:
    raise('Wrong number of arguments to script!')

# Creating the CSV file
csv_fid = open(csv_filename, 'w')
csv_fid.write('Mask ID,STG accuracy,STG mean RT,STG std RT,STI accuracy,STI mean duration,STI std duration,xth percentile STG RT,Corrected SSRT,Lowest block STG Acc,Lowest block STI accuracy,How many blocks under ' + str(qcSTGAcc) + '% STG accuracy\n')

for txtFile in files:
    subj = txtFile[:-4]
    print 'Analyzing mask ID ' + subj
    # Open data
    data = np.recfromtxt(txtFile, delimiter='\t')

    # Computes the delay (in ms) to augment the trial onset. If the time entered at the beginning of the task is the same as the length of the TR (e.g. 2000), then blockStartCol should happen 4 times the time entered according to the E-prime script. Since we have 4 dummy TRs, and assuming we crop out the first 4 TRs in fMRI preprocessing, then this delay equals to 0. However, we've been conservative and have been using 2300 in the begining, even though our TR is 2000. That means that when we crop the fMRI data after the first 4 TRs (8000 ms), our task only actually began at 4 * 2300 = 9200. The delay below corresponds to that difference.
    idjEnteredTR = np.nonzero(data[0, :] == trLengthCol)[0]
    enteredTRLength = int(data[2, idjEnteredTR][0])
    delay = numDummyTRs * (enteredTRLength - actualTRLength)

    # Figure out how many blocks we have, based on the variable that stores the offset of the waiting period
    idjBlockStart = np.nonzero(data[0, :] == blockStartCol)[0]
    # we add one because the matrix we loop through removes the headers
    blockStartRows = [i + 1 for i, s in enumerate(data[1:, idjBlockStart]) if len(s[0]) > 1]
    if len(blockStartRows) != 4:
        print 'WARNING: FOUND', len(blockStartRows), 'BLOCKS!!!'

    # Make sure we have all the trials we are expecting
    idjBlockNum = np.nonzero(data[0, :] == trialBlockCol)[0]
    rowsPerBlock = []
    for blockIdx, blockRow in enumerate(blockStartRows):
        # Get the number of the block and all the rows that correspond to that block. They start on the row right after where the block started
        blockNum = data[blockRow + 1, idjBlockNum]
        blockTrials = [(blockRow + i) for i, s in enumerate(data[blockRow:, idjBlockNum]) if s[0] == blockNum]
        # For merged files, it can happen that the same block number is used in two different blocks, so let's only take the consectuive indexes as the trials for this particular block
        nonConsec = np.nonzero(np.diff(blockTrials) > 1)[0]
        if len(nonConsec) > 0:
            blockTrials = blockTrials[:(nonConsec[0] + 1)]
        if len(blockTrials) != expectedTrialNum:
            print 'WARNING!!! Found', len(blockTrials), 'trials in block', (blockIdx + 1)
        rowsPerBlock.append(blockTrials)

    # Let's create one stim_file per condition
    stim_fids = []
    for cond in condNames:
        stim_fids.append(open(subj + '_' + cond + '.txt', 'w'))

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
    for bidx, trials in enumerate(rowsPerBlock):
        # We only analyze blocks for which we have all expected trials
        if len(trials) == expectedTrialNum:
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

            # Finally, compute onset times for each condition
            blockOnset = int(data[blockStartRows[bidx], idjBlockStart][0])
            for c, cond in enumerate(condNames):
                idjOnset = np.nonzero(data[0, :] == condOnsetCol[c])[0]
                if cond == 'STG-correct':
                    onsets = [int(i) for i in data[correctGoTrials, idjOnset]]
                elif cond == 'STG-incorrect':
                    onsets = [int(i) for i in data[incorrectGoTrials, idjOnset]]
                elif cond == 'STI-correct':
                    onsets = [int(i) for i in data[correctInhTrials, idjOnset]]
                elif cond == 'STI-incorrect':
                    onsets = [int(i) for i in data[incorrectInhTrials, idjOnset]]
                else:
                    # this is for blank trials, which we haven't found yet
                    blankTrials = [trials[i] for i, s in enumerate(data[trials, idjTrialType]) if s == 'StBTrial']
                    onsets = [int(i) for i in data[blankTrials, idjOnset]]

                # remove offset and delay, and convert to seconds
                onsets = (np.array(onsets) - blockOnset + delay) / float(1000)
                for t in onsets:
                    stim_fids[c].write('%.2f ' % t)
                stim_fids[c].write('\n')

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
    subjXthPercentile = (stgRT[ul] + stgRT[ll]) / float(2)
    subjSSRT = subjXthPercentile - subjStiMeanDur

    # Spit out columns to CSV file
    csv_fid.write(subj + ',')
    csv_fid.write(','.join([str(i) for i in [subjStgAcc, subjStgMeanRT, subjStgStdRT, subjStiAcc, subjStiMeanDur, subjStiStdDur, subjXthPercentile, subjSSRT, np.min(stgAcc), np.min(stiAcc), np.sum(np.array(stgAcc) < qcSTGAcc)]]))
    csv_fid.write('\n')

    # Output to the screen if we only ran it for one subject
    if len(files) == 1:
        print '=== Mean over good blocks ==='
        print 'STG accuracy:', subjStgAcc
        print 'STG RT:', subjStgMeanRT, '+-', subjStgStdRT
        print 'STI accuracy:', subjStiAcc
        print 'STI duration:', subjStiMeanDur, '+-', subjStiStdDur
        print 'xth percentile STG RT:', subjXthPercentile
        print 'Corrected SSRT:', subjSSRT
        b = 0
        for bidx, trials in enumerate(rowsPerBlock):
            if len(trials) == expectedTrialNum:
                print '=== BLOCK', bidx + 1, '==='
                print 'STG accuracy:', stgAcc[b]
                print 'STG RT:', stgMeanRT[b], '+-', stgStdRT[b]
                print 'STI accuracy:', stiAcc[b]
                b += 1

    # closing all open files
    for c in range(len(condNames)):
        stim_fids[c].close()
csv_fid.close()
