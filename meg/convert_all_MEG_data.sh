#!/bin/bash
# Script that converts .ds data to .fif
#
# Gustavo Sudre, 01/2013
# Updated in 03/2014 to add log file

dataDir='/mnt/neuro/MEG_data/raw/'
outDir='/mnt/neuro/MEG_data/fifs/stop/'
log_file='/Users/sudregp/fifs.log'
# task='rest'
task='stop'

dates=`ls $dataDir`
# for each directory in dataDir, get the list of files in it
for d in $dates 
do
	files=`ls $dataDir/$d`
	# for each file in the date folder, only run MNE if it's rest and it's 
	# not filtered
	for f in $files 
	do
		splitTask=(`echo $f | tr '_' ' '`)
		splitRaw=(`echo $f | tr '-' ' '`)
		# fname="$splitTask"_"$task"_LP100_CP3_DS300_raw.fif
		fname="$splitTask"_"$task"_raw.fif
		echo Working on ${fname}
		if [ -e ${outDir}/${fname} ]; then
			echo "$splitTask",exists >> ${log_file}
		elif [ ${splitTask[1]} == $task ] && [ ${splitRaw[0]} == $f ]; then
			# note that we always convert the first version of the file. If we want the second one, we need to run the commands manually
			# mne_ctf2fiff --ds $dataDir/$d/$f/ --fif tmp.fif
			# mne_rename_channels --fif tmp.fif --alias ~/.mne/renameUPT001toSTI104.txt
			# mne_process_raw --raw tmp.fif --projoff --lowpass 100 --decim 2 --grad 3 --save ${outDir}/${fname}
			# mne_process_raw --raw tmp.fif --projoff --filteroff --grad 3 --save ${outDir}/${fname}
			mne_ctf2fiff --ds $dataDir/$d/$f/ --fif ${outDir}/${fname}
			if [ -e ${outDir}/${fname} ]; then
				echo "$splitTask",success >> ${log_file}
			else
				echo "$splitTask",error >> ${log_file}
			fi
		fi
	done
done
rm tmp.fif
