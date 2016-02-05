#!/bin/bash
# Script to run a regression analysis in all voxels.

##### BEGIN EDITABLE VARIABLES #####

covariates_file='/Users/sudregp/tmp/sx_adhd_regana.txt'

conditions=(STG-correct STG-incorrect STI-correct STI-incorrect)

output_dir='/Users/sudregp/tmp/'

# leave it empty if not using masks
# mask=''
mask='/mnt/neuro/MR_behavioral/stop_task_analysis/whole_brain_analysis/group_level_mask+tlrc'

##### END OF EDITABLE VARIABLES #####

# run the analysis for each condition
for c in ${conditions[@]}; do
    cmd_line=''
    # for each subject in the file
    while read line; do
        split_line=(`echo $line | tr '\t' ' '`)
        s=${split_line[0]}
        s=${s/stats./}
        # skip the header
        if [ $s != 'mask_id' ]; then
            subj_line='/mnt/neuro/data_by_maskID/'${s}'/afni/'${s}'.stop.results/stats.'${s}'+tlrc['${c}'#0_Coef]'
            cmd_line=${cmd_line}' '${subj_line}
        fi
    done < $covariates_file
    # echo $rows $cols
    # echo $cmd_line
    cmd_line='3dttest++ -prefix '${output_dir}'/'${c}'_regression_out -setA '$cmd_line' -covariates '${covariates_file}
    if [ $mask != '' ]; then
        cmd_line=$cmd_line' -mask '$mask
    fi
    echo $cmd_line
    $cmd_line
done