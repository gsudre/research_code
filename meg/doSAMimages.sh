#!/bin/bash
# Script to generate source images of SAM estimates so we can check for outliers. Only works for subjects we have already processed usinf SAM!

##### BEGIN EDITABLE VARIABLES #####

# ds='/mnt/neuro/MEG_data/raw/20110416/NBLWONNX_rest_20110416_01-f.ds/'
mri_path='/mnt/neuro/MEG_structural/afni/'

split_path=(`echo $ds | tr '/' ' '`)
split_path=(`echo ${split_path[5]} | tr '_' ' '`)
subj_name=${split_path[0]}

SAMsrc -r $ds -c good_data,1-58Hz -x '-10 12' -y '-8 8' -z '0 14' -s 0.5 -u 4 -v -p -U1
adwarp -apar ${mri_path}/${subj_name}/ortho+tlrc -dpar ${ds}/SAM/good_data,1-58Hz,U1.svl -dxyz 5 -prefix ${subj_name}_image_U1