! /bin/bash

# Script to change the structural MRI in the scratch file to 1 mm isotropic resolution and to fix the image size to the reference size so that it will be read into Matlab using the correct coordinates. I will also unzip the file as well.

flirt -in /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1.nii -ref /Volumes/rbraid/mr_data/tonya/scripts_quality_assurance_at_9/t1_ref.nii.gz -applyisoxfm 1 -out /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1_iso.nii.gz

bet2 /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1_iso.nii.gz /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1_brain_mask_iso.nii.gz

3dedge3 -input /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1.nii_iso.gz -prefix /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1edge_iso.nii.gz

gunzip /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1_iso.nii.gz
gunzip /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1_brain_mask_iso.nii.gz
gunzip /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1edge_iso.nii.gz
