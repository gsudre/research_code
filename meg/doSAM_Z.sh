#!/bin/bash
# Script to run SAM analysis and generate weights for each subject

##### BEGIN EDITABLE VARIABLES #####

# ds='/mnt/neuro/MEG_data/raw/20110416/NBLWONNX_rest_20110416_01-f.ds/'
mri_path='/mnt/neuro/MEG_structural/afni/'

split_path=(`echo $ds | tr '/' ' '`)
split_path=(`echo ${split_path[5]} | tr '_' ' '`)
subj_name=${split_path[0]}
log_file=${subj_name}_SAM.log

# checks if we have a hull already
if [ ! -e ${mri_path}/${subj_name}/ortho.shape ]; then
    echo 'Could not find ortho.shape for '$subj_name > $log_file
elif [ ! -e ${mri_path}/${subj_name}/ortho+tlrc.HEAD ]; then
    echo 'Could not find ortho+tlrc for '$subj_name > $log_file
else
    # localSpheres -d $ds -s ${mri_path}/${subj_name}/ortho.shape -M -v | tee $log_file
    # inflateSpheres $ds | tee -a $log_file
    # checkSpheres -v $ds | tee -a $log_file
    ipython ~/research_code/meg/generate_SAM_cov_windows.py $ds
    mv $ds/SAM/good_data $ds/SAM/good_data_Z
    if [ -e $ds/bad.segments ]; then 
        mv $ds/bad.segments $ds/bad.segments.old
    fi
    SAMcov -r $ds -f "1 58" -m good_data_Z -v | tee -a $log_file
    # Vecwarp -apar ${mri_path}/${subj_name}/ortho+tlrc -input targetsInTLR.txt -backward > tmp
    # Vecwarp -matvec toPRI.txt -input tmp > ${ds}/SAM/targets
    SAMsrc -r $ds -c good_data_Z,1-58Hz -t targets -u 4 -v -Z -W 0 | tee -a $log_file
    echo 'Converting weights'
    dumpSAMFile ${ds}/SAM/good_data_Z,1-58Hz,targets.wts > tmp
    ipython ~/research_code/meg/read_SAM_weights.py tmp $subj_name
fi