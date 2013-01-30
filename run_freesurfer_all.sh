#!/bin/bash
# Script that runs Freesurfer for all AFNI subjects
#
# Gustavo Sudre, 01/2013

AFNI_folder="$HOME/MEG_structural/afni"
spacing=5
model_script="$HOME/research_code/MEG_sensor2mneSourceSpace.sh"

# for all subjects in the afni folder, check if there is already a Freesurfer
# subject folder. If not, start the process
afni_subjects=`ls $AFNI_folder`
for subj in $afni_subjects
do
	if [ ! -d $SUBJECTS_DIR/$subj ]; then
		3dcopy $AFNI_folder/$subj/ortho+orig "$subj"_ortho.nii
		bash $model_script $subj $spacing "$subj"_ortho.nii
		
		# if we have a dense head surface in the end, then the script was
		# successful running until the end (no claims about the quality of
		# reconstruction!). Then, we can collect the gargabe. If not, add 
		# to the list of problems
		if [ -f $SUBJECTS_DIR/$subj/bem/"$subj"-head-dense.fif ]; then
			# move the logs in the end for garbage collection
			mv "$subj"_mne_model.log "$subj"_surface.log $SUBJECTS_DIR/$subj/
			mv "$subj"_ortho.nii $AFNI_folder/$subj/
		else
			echo $subj >> "$AFNI_folder"/problems.log
		fi
	fi
done 
