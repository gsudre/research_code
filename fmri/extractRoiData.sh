#!/bin/bash
# Script to extract the regressions coefficients (#0_Coef) for different conditions and different ROI+hemisphere combinations. It outputs the data to a text file in output_dir. There is one text file for each combination of condition x roi x hemisphere, where each row in the file corresponds to the data of a given subject listed in subjects_file (one subjects per line).

##### BEGIN EDITABLE VARIABLES #####

subjects_file='/Users/sudregp/tmp/subjs.txt'

hemi=(left right)

# VLPFC = BA44,45,47
# ACC = BA24,32,33
rois=(brodmannArea44 brodmannArea45 brodmannArea47 putamen accumbens caudate brodmannArea24 brodmannArea32 brodmannArea33)

conditions=(STG-correct STG-incorrect STI-correct STI-incorrect)

output_dir='/Users/sudregp/tmp/'

##### END OF EDITABLE VARIABLES #####

# define where to find the atlas based on AFNI location
sys_name=`uname`
if [ $sys_name = 'Linux' ]; then
    afni_location='/usr/local/neuro/afni_linux_openmp_64/'
else
    afni_location='/Applications/afni/'
fi

# for each combination of ROI and condition, create the headers.
# Note that this erases previous files with the same name!
for r in ${rois[@]}; do
    for c in ${conditions[@]}; do
        for h in ${hemi[@]}; do
            fname=${output_dir}/roiData_${h}_${r}_${c}.txt
            echo MaskID Mean NZMean NZCount NZMin NZMax > $fname
        done
    done
done

# for each subject in the file
while read s; do 
    echo 'Working on subject' $s
    # resample the stats file to match the atlas grid
    cd /mnt/neuro/data_by_maskID/${s}/afni/${s}.stop.results
    3dresample -overwrite -master ${afni_location}/TT_N27+tlrc -prefix stats_resampled+tlrc -inset stats.${s}+tlrc
    # for each combination of ROI and condition
    for r in ${rois[@]}; do
        for c in ${conditions[@]}; do
            for h in ${hemi[@]}; do
                fname=${output_dir}/roiData_${h}_${r}_${c}.txt
                res=`3dROIstats -quiet -nzmean -nzminmax -nzvoxels -mask TT_Daemon:${h}:${r} stats_resampled+tlrc[${c}#0_Coef]`
                echo $s $res >> $fname
            done
        done
    done
    rm stats_resampled+tlrc*
done < $subjects_file