#!/bin/bash
# Script to run BET2 and the afni program 3D edge to detect the edges in an
# image
# data_dir='/Users/sudregp/tmp/tonya/'

bet2 ${data_dir}/t1.nii.gz ${data_dir}/t1_brain_mask.nii.gz

3dedge3 -input ${data_dir}/t1.nii.gz -prefix ${data_dir}/t1_edge.nii.gz

gunzip ${data_dir}/t1.nii.gz
gunzip ${data_dir}/t1_brain_mask.nii.gz
gunzip ${data_dir}/t1_edge.nii.gz
