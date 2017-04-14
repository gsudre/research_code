#!/bin/bash
# Script to change the structural MRI in the scratch file to 1 mm isotropic
# resolution and to fix the image size to the reference size so that it will be
# read into Matlab using the correct coordinates. I will also unzip the file as
# well.
# data_dir='/Users/sudregp/tmp/tonya/'
# template_1mm='/usr/local/fsl/data/standard/MNI152_T1_1mm.nii.gz'

flirt -in ${data_dir}/t1.nii -ref $template_1mm -applyisoxfm 1 \
      -out ${data_dir}/t1_iso.nii.gz

bet2 ${data_dir}/t1_iso.nii.gz ${data_dir}/t1_brain_mask_iso.nii.gz

3dedge3 -input ${data_dir}/t1_iso.nii.gz -prefix ${data_dir}/t1_edge_iso.nii.gz

gunzip ${data_dir}/t1_iso.nii.gz
gunzip ${data_dir}/t1_brain_mask_iso.nii.gz
gunzip ${data_dir}/t1_edge_iso.nii.gz
