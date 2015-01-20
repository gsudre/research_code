#!/bin/bash
# Script to run SAM analysis and generate weights for each subject

##### BEGIN EDITABLE VARIABLES #####

# ds='/mnt/neuro/MEG_data/raw/20110416/NBLWONNX_rest_20110416_01-f.ds/'
mri_path='/mnt/neuro/MEG_structural/afni/'

split_path=(`echo $ds | tr '/' ' '`)
split_path=(`echo ${split_path[5]} | tr '_' ' '`)
subj_name=${split_path[0]}
log_file=${subj_name}_SAM_narrow.log
bands=( 1-4 4-8 8-13 13-30 30-55 65-100 )

# checks if we have a hull already
if [ ! -e ${mri_path}/${subj_name}/ortho.shape ]; then
    echo 'Could not find ortho.shape for '$subj_name > $log_file
elif [ ! -e ${mri_path}/${subj_name}/ortho+tlrc.HEAD ]; then
    echo 'Could not find ortho+tlrc for '$subj_name > $log_file
else
    # # We already did these steps once, no need to redo them
    # localSpheres -d $ds -s ${mri_path}/${subj_name}/ortho.shape -M -v | tee $log_file
    # inflateSpheres $ds | tee -a $log_file
    # checkSpheres -v $ds | tee -a $log_file
    ipython ~/research_code/meg/generate_SAM_cov_windows.py $ds
    if [ -e $ds/bad.segments ]; then 
        mv $ds/bad.segments $ds/bad.segments.old
    fi
    Vecwarp -apar ${mri_path}/${subj_name}/ortho+tlrc -input tlrc_seeds_targets_RAI.txt -backward > tmp
    Vecwarp -matvec toPRI.txt -input tmp > ${ds}/SAM/targets
    for b in "${bands[@]}"; do
        split_band=(`echo $b | tr '-' ' '`)
        lb=${split_band[0]}
        hb=${split_band[1]}
        # this version relaxes the limited bandwith problem
        /usr/local/neuro/bin/SAMcov -r $ds -f "$lb $hb" -m good_data -v | tee -a $log_file
        SAMsrc -r $ds -c good_data,${lb}-${hb}Hz -t targets -u 4 -v -Z -W 0 | tee -a $log_file
        if [ -e ${ds}/SAM/good_data,${lb}-${hb}Hz,targets.wts ]; then
            echo 'Converting weights'
            dumpSAMFile ${ds}/SAM/good_data,${lb}-${hb}Hz,targets.wts > tmp
            ipython ~/research_code/meg/read_SAM_weights.py tmp ${subj_name}_${lb}-${hb}
        fi
    done
fi



