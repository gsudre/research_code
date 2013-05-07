#!/bin/bash
# Script that converts .ds data to .fif for specific subjects. Takes in ds folder and destination folder
#
# Gustavo Sudre, 01/2013

dsDir=$1
outDir=$2

splitUnderscore=(`echo $dsDir | tr '_' ' '`)
# when we split with the underscore, the third to last item is the task, and the one before that, when we split on /, the last item is the subject name
fileLength=${#splitUnderscore[@]}                                          
last2P=$((fileLength - 3))
task=${splitUnderscore[${last2P}]}

restOfIt=$((fileLength - 4))
splitDash=(`echo ${splitUnderscore[$restOfIt]} | tr '/' ' '`)
fileLength=${#splitDash[@]}                                          
lastP=$((fileLength - 1))
subjectCode=${splitDash[${lastP}]}

mne_ctf2fiff --ds $dsDir --fif tmp.fif
mne_rename_channels --fif tmp.fif --alias ~/.mne/renameUPT001toSTI104.txt
mne_process_raw --raw tmp.fif --projoff --lowpass 58 --highpass 0.5 --decim 2 --grad 3 \
				--save "$outDir"/"$subjectCode"_"$task"_LP58_HP.5_CP3_DS300_raw.fif
# we need a copy without HP so the movement channels stay intact
mne_process_raw --raw tmp.fif --projoff --lowpass 100 --decim 2 --grad 3 \
                --save "$outDir"/"$subjectCode"_"$task"_LP100_CP3_DS300_raw.fif
rm tmp.fif
