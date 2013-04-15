#!/bin/bash
# Script that runs Freesurfer new subjects. Takes subject MEG code and MPRage folder as parameters
#
# Gustavo Sudre, 04/2013

subj=$1
mprageDir=$2
AFNI_folder="/mnt/neuro/MEG_structural/afni"
spacing=5
model_script="$HOME/research_code/MEG_sensor2mneSourceSpace.sh"

mkdir $AFNI_folder/$subj/
cd $mprageDir
to3d -prefix anat -session $AFNI_folder/$subj/ *.dcm
cd /tmp
3dcopy "$AFNI_folder"/"$subj"/anat+orig "$subj"_anat.nii
bash $model_script $subj $spacing "$subj"_anat.nii
mv "$subj"_mne_model.log "$subj"_surface.log $SUBJECTS_DIR/$subj/
mv "$subj"_anat.nii $AFNI_folder/$subj/

