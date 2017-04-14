#! /bin/bash

# Script to run BET2 and the afni program 3D edge to detect the edges in an image

bet2 /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1.nii.gz /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1_brain_mask.nii.gz

3dedge3 -input /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1.nii.gz -prefix /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1edge.nii.gz

gunzip /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1.nii.gz
gunzip /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1_brain_mask.nii.gz
gunzip /Volumes/rbraid/mr_data/tonya/structural_at_9_scratch_file/t1edge.nii.gz
