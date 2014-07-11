#!/bin/bash
# Script to run a regression analysis in all voxels.

##### BEGIN EDITABLE VARIABLES #####

covariates_file='/Users/sudregp/tmp/sx_adhd_regana.txt'

conditions=(STG-correct STG-incorrect STI-correct STI-incorrect)

output_dir='/Users/sudregp/tmp/'

# how significantly inatt (column 1) predicts BOLD response, taking into account (i.e. covarying for) sex and age (columns 4 and 5)
model='1:0 2 3'

##### END OF EDITABLE VARIABLES #####

# run the analysis for each condition
for c in ${conditions[@]}; do
    cmd_line=''
    rows=0
    # for each subject in the file
    while read line; do
        split_line=(`echo $line | tr '\t' ' '`)
        s=${split_line[0]}
        cols=0
        # skip the header
        if [ $s != 'mask_id' ]; then
            let rows=rows+1
            subj_line='-xydata'
            subj_data='/mnt/neuro/data_by_maskID/'${s}'/afni/'${s}'.stop.results/stats.'${s}'+tlrc['${c}'#0_Coef]'
            for d in ${split_line[@]}; do
                if [ $d != $s ]; then
                    subj_line=${subj_line}' '${d}
                    let cols=cols+1
                fi
            done
            subj_line=${subj_line}' '${subj_data}
            cmd_line=${cmd_line}' '${subj_line}
        fi
    done < $covariates_file
    # echo $rows $cols
    # echo $cmd_line
    cmd_line='3dRegAna -rows '$rows' -cols '$cols' -bucket 0 '${c}'_regression_out '$cmd_line' -model '$model
    echo $cmd_line
    $cmd_line
done