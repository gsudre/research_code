import numpy as np
import math
import sys
import glob
import matplotlib.pyplot as plt

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

# files = ['/Volumes/neuro/MR_behavioral/cleaned_data/0440.txt']
# Creating the CSV file
csv_fid = open(csv_filename, 'w')
csv_fid.write('Mask ID,STG accuracy,STG mean RT,STG std RT,STI accuracy,STI mean duration,STI std duration,xth percentile STG RT,Corrected SSRT,Lowest block STG Acc,Lowest block STI accuracy,How many blocks under ' + str(qcSTGAcc) + '% STG accuracy,slope,B1 STG accuracy,B1 STG mean RT,B1 STG std RT,B1 STI accuracy,B1 STI mean dur,B1 STI std dur,B2 STG accuracy,B2 STG mean RT,B2 STG std RT,B2 STI accuracy,B2 STI mean dur,B2 STI std dur,B3 STG accuracy,B3 STG mean RT,B3 STG std RT,B3 STI accuracy,B3 STI mean dur,B3 STI std dur,B4 STG accuracy,B4 STG mean RT,B4 STG std RT,B4 STI accuracy,B4 STI mean dur,B4 STI std dur\n')

for txtFile in files:
    subj = txtFile[:-4]
    print 'Analyzing mask ID ' + subj
    # Open data
    data = np.recfromtxt(txtFile, delimiter='\t')

    # Computes the delay (in ms) to augment the trial onset. If the time entered at the beginning of the task is the same as the length of the TR (e.g. 2000), then blockStartCol should happen 4 times the time entered according to the E-prime script. Since we have 4 dummy TRs, and assuming we crop out the first 4 TRs in fMRI preprocessing, then this delay equals to 0. However, we've been conservative and have been using 2300 in the begining, even though our TR is 2000. That means that when we crop the fMRI data after the first 4 TRs (8000 ms), our task only actually began at 4 * 2300 = 9200. The delay below corresponds to that difference.
    idjEnteredTR = np.nonzero(data[0, :] == trLengthCol)[0]
    idiEnteredTR = np.nonzero(data[1:, idjEnteredTR] != '')[0]
    if len(idiEnteredTR) == 0:
        print 'WARNING!!! Could not find entered TR length. Assuming 2300. Check original files!'
        enteredTRLength = 2300
    else:
        enteredTRLength = int(data[idiEnteredTR + 1, idjEnteredTR][0])
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
    slopeX = []
    slopeY = []
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
            for i in correctInhTrials:
                slopeX.append(int(data[i, idjStiDur][0]))
                slopeY.append(1)
            for i in incorrectInhTrials:
                slopeX.append(int(data[i, idjStiDur][0]))
                slopeY.append(0)

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
                # if there are no trials in this run for the condition, add *
                if len(onsets) == 0:
                    stim_fids[c].write('*')
                # if there is only one trial, add the * so we don't confuse file formats (see http://afni.nimh.nih.gov/pub/dist/doc/misc/Decon/DeconSummer2004.html), which can happen in the case of only one trial in every block
                elif len(onsets) == 1:
                    stim_fids[c].write('%.2f *' % onsets[0])
                else:
                    for t in onsets:
                        stim_fids[c].write('%.2f ' % t)
                stim_fids[c].write('\n')

    # Now we interpolate to get SSRT. First, order correctGoTrials based on RT, then choose the number relative to the STI accuracy
    # just flattening the lists first
    oldStiDur = stiDur
    stgRT = np.sort([i for j in stgRT for i in j])
    stiDur = np.sort([i for j in stiDur for i in j])

    # Now we compile everything across blocks.
    subjStgMeanRT = np.mean(stgRT)
    subjStgStdRT = np.std(stgRT)
    subjStiMeanDur = np.mean(stiDur)
    subjStiStdDur = np.std(stiDur)
    subjStgAcc = np.mean(stgAcc)
    subjStiAcc = np.mean(stiAcc)

    if len(stgRT) > 0:
        ll = int(math.floor(subjStiAcc / 100 * len(stgRT)))
        ul = int(math.ceil(subjStiAcc / 100 * len(stgRT)))
        # if this is the case, then something clearly went wrong and the subject will be thrown away because of something else. This if statement is here just so the script doesn't break.
        if ul == len(stgRT):
            print 'WARNING: Subject upper accuracy limit is is out of range!'
            ul = ul - 1
        subjXthPercentile = (stgRT[ul] + stgRT[ll]) / float(2)
        subjSSRT = subjXthPercentile - subjStiMeanDur

        # Spit out columns to CSV file
        block_stats = []
        b = 0
        for bidx, trials in enumerate(rowsPerBlock):
            if len(trials) == expectedTrialNum:
                block_stats.append(stgAcc[b])
                block_stats.append(stgMeanRT[b])
                block_stats.append(stgStdRT[b])
                block_stats.append(stiAcc[b])
                block_stats.append(np.mean(oldStiDur[b]))
                block_stats.append(np.std(oldStiDur[b]))
                b += 1

        # Calculating slope of stiDur vs accuracy plot
        Xaxis = range(210, 800, 16)
        Yaxis = np.empty([len(Xaxis)])
        for ix, x in enumerate(Xaxis):
            Yaxis[ix] = np.sum(np.all([[np.array(slopeX) == x], [np.array(slopeY) == 1]], axis=0))
        fig = plt.figure()
        xp = np.linspace(210, 800, 100)
        z = np.polyfit(Xaxis, Yaxis, 1)
        slope = z[0]
        pn = np.poly1d(z)
        plt.plot(Xaxis, Yaxis, 'o', Xaxis, pn(Xaxis), '--')
        plt.ylabel('Num correct trials')
        plt.xlabel('STI Duration')
        plt.title(subj)
        fig.savefig(subj + '.png', format='png')

        csv_fid.write(subj + ',')
        csv_fid.write(','.join([str(i) for i in [subjStgAcc, subjStgMeanRT, subjStgStdRT, subjStiAcc, subjStiMeanDur, subjStiStdDur, subjXthPercentile, subjSSRT, np.min(stgAcc), np.min(stiAcc), np.sum(np.array(stgAcc) < qcSTGAcc), slope, block_stats]]))

        csv_fid.write('\n')
    else:
        print 'WARNING!!! Did not find any trials for STG. Check for errors!'

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
