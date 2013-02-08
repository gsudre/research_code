#!/bin/bash
# Given a temporary folder and a destination folder, organizes the files downloaded form the DICOM server.
#
# Usage: sort_mr_data /tmp/ /usr/local/neuro/MR_data/  
#
# Gustavo Sudre, 02/2013

TEMP_FOLDER=$1
MR_DATA_FOLDER=$2

dicoms=`ls "$TEMP_FOLDER"/*-DICOM*`
echo "Found these DICOM files in $TEMP_FOLDER: "
for file in $dicoms
do
    echo $file
done

read -p "Press any key to start sorting, or Ctrl+C to quit..."

# For each DICOM
for file in $dicoms
do
    # strip out the components of the filename
    bar=(`echo $file | tr '-' ' '`)
    subject="${bar[0]}"
    subject=(`echo $subject | tr '/' ' '`)
    subjectLength=${#subject[@]}                                          
    lastP=$((subjectLength - 1))
    subjectName=${subject[${lastP}]}
    mrn="${bar[1]}"
    scanId="${bar[3]}"

    target_name="$MR_DATA_FOLDER"/"$subjectName"-"$mrn"/
    # if we already have the MRN in our tree, that's our target directory
    if [ ! -d $target_name ]; then
        mkdir $target_name
    fi

    # Unpack the DICOMs to the tree
    echo "Unpacking $file"
    # do it differently whether it's gzipped or not
    if [ "${bar[4]}" == "DICOM.tgz" ]; then
        tar -zxf $file -C $MR_DATA_FOLDER
    else
        tar -xf $file -C $MR_DATA_FOLDER
    fi

    # Remove leading zeros from scanID
    scanId="$(echo $scanId | sed 's/^0*//')"

    rtData=`ls "$TEMP_FOLDER"/E"$scanId".*`
    bar=(`echo $rtData | tr '.' ' '`)
    barLength=${#bar[@]}                                          
    lastP=$((barLength - 1))
    ext=${bar[${lastP}]}
    if [ "$ext" == 'tgz' ]; then
        echo "Unpacking $rtData"
        tar -zxf $rtData -C $target_name
    elif [ "$ext" == 'tar' ]; then
        echo "Unpacking $rtData"
        tar -xf $rtData -C $target_name
    else
        echo "WARNING: Could not find real-time data!"
    fi
done
    # Look for the realtime data

    # IF found, unpack it to the tree as well

# Grab the examNumber and check if we have already downloaded it

# Download the .tar.gz of DICOMs

# Download the .tgz of RT data

# Unpack the tarballs to our tree

# Remove temporary downloaded tarballs