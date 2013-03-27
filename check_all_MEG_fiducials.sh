#!/bin/bash
# Script that checks if the fiducials are correctly placed in all MEG data
#
# Gustavo Sudre, 03/2013

dataDir='/usr/local/neuro/MEG_data/raw/'
task='rest'

dates=`ls $dataDir`
# for each directory in dataDir, get the list of files in it
for d in $dates 
do
	files=`ls $dataDir/$d`
	# for each file in the date folder, only run check if it's rest and it's 
	# not filtered
	for f in $files 
	do
		splitTask=(`echo $f | tr '_' ' '`)
		splitRaw=(`echo $f | tr '-' ' '`)
		if [ ${splitTask[1]} == $task ] && [ ${splitRaw[0]} == $f ]; then
			python check_fiducials.py $dataDir/$d/$f/
		fi
	done
done

