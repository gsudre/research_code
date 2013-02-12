#!/bin/bash
# Sorts the MR data Liv sent us into our directory structure
#
# Usage: sort_mr_data_Liv ~/MR_data/LivTest /usr/local/neuro/MR_data/  
#
# Gustavo Sudre, 02/2013

DICOM_FOLDER="$1/DICOM/"  # whatever has DICOM and RealTime
RT_FOLDER="$1/RealTime/"  # whatever has DICOM and RealTime
MR_DATA_FOLDER=$2
TMP_FOLDER="tmp12345"

dicoms=`ls "$DICOM_FOLDER"/*`

# just to assure we don't have anything else in the folder
mkdir $TMP_FOLDER
cd $TMP_FOLDER

for file in $dicoms
do
    echo "Working on $file"
    # For each DICOM we have, uncompress the file
    tar -xf $file

    # From the resulting directory name, we can get the info we need
    myDirToMove=`ls -d *-*`
    myDir=`ls $myDirToMove`
    bar=(`echo $myDir | tr '-' ' '`)
    scanId="${bar[1]}"
    
    bar=(`echo $file | tr '/' ' '`)
    fileLength=${#bar[@]}                                          
    lastP=$((fileLength - 1))
    filename=${bar[${lastP}]}

    bar=(`echo $filename | tr '.' ' '`)
    maskId="${bar[1]}"

    # Move the unzipped DICOM folder to our MR structure, but first create
    # the maskID inside it
    mkdir "$maskId"
    mv "$myDirToMove"/* "$maskId"
    mv "$maskId" "$myDirToMove"/
    # If the folder already exists, than we already have data for the patient
    if [ -d "$MR_DATA_FOLDER"/"$myDirToMove" ]; then
        # only move the data if it's a new maskId
        if [ ! -d "$MR_DATA_FOLDER"/"$myDirToMove"/"$maskId" ]; then
            mv "$myDirToMove"/* "$MR_DATA_FOLDER"/"$myDirToMove"
            rmdir "$myDirToMove"
            moved=1
        else
            echo "MaskId already in MR folder!"
            rm -rf "$myDirToMove"
            moved=0
        fi
    else
        mv -f "$myDirToMove" "$MR_DATA_FOLDER"
        moved=1
    fi

    if [ $moved -eq 1 ]; then
        # Try to find real-time data labeled to match the DICOM
        rtFiles=`ls "$RT_FOLDER"/*."$maskId".E"$scanId"*`
        for fileMatch in $rtFiles
        do
            echo "Found matching real time $fileMatch"
            tar -xf $fileMatch -C "$MR_DATA_FOLDER"/"$myDirToMove"/"$maskId"

            # cleaning up
            rm $fileMatch
        done
    fi

    # cleaning up original DICOM file
    rm $file 
done

cd ..
rm -rf $TMP_FOLDER