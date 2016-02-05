#!/bin/bash
# Script to run a regression analysis in all voxels.

##### BEGIN EDITABLE VARIABLES #####

covariates_file='/Users/sudregp/data/fmri/joel_sx.txt'
output_dir='/Users/sudregp/tmp/'
model='1:0'
roi=16

##### END OF EDITABLE VARIABLES #####
cmd_line=''
rows=0
# for each subject in the file
while read line; do
    split_line=(`echo $line | tr '\t' ' '`)
    s=${split_line[0]}
    cols=0
    # skip the header
    if [ $s != 'maskid' ]; then
        let rows=rows+1
        subj_line='-xydata'
        subj_data='/Users/sudregp/data/results/fmri_72ROIsJoel/Zcorr_'${s}'_'${roi}'+tlrc'
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
cmd_line='3dRegAna -rows '$rows' -cols '$cols' -bucket 0 regression_out '$cmd_line' -model '$model
echo $cmd_line
$cmd_line