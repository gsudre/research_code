#!/bin/bash
# Gets all Freesurfer parcellations (area, thickness, volume, subcortical) for
# list of subjects.
# This script is just like the other ones, but it extracts the Destrieux atlas
# (a2009s), which has more ROIs.
#
# GS, 10/2019

# (from https://surfer.nmr.mgh.harvard.edu/fswiki/FsTutorial/AnatomicalROI)

printf "\nLooking at $SUBJECTS_DIR for data."

printf "\n\nUse Ctrl+C to cancel, and\n\texport SUBJECTS_DIR=my_dir \nif incorrect.\n\n"

# if there are no comman-line arguments, do it for all subjects
if [ "$#" -eq 0 ]; then
    echo "No list of mask ids used: processing all subjects.";
    sfile=subjects_file.txt
    ls -1 $SUBJECTS_DIR/ > $sfile
else
    sfile=$1
fi

nscans=`cat $sfile | wc -l`
echo "Found $nscans scan(s) requested for processing."

python2_bin=`which python2`;

$python2_bin $FREESURFER_HOME/bin/aparcstats2table --subjectsfile=$sfile --hemi lh --meas thickness --tablefile lh_thickness.txt --skip -p aparc.a2009s
$python2_bin $FREESURFER_HOME/bin/aparcstats2table --subjectsfile=$sfile --hemi rh --meas thickness --tablefile rh_thickness.txt --skip -p aparc.a2009s
$python2_bin $FREESURFER_HOME/bin/aparcstats2table --subjectsfile=$sfile --hemi rh --meas area --tablefile rh_area.txt --skip -p aparc.a2009s
$python2_bin $FREESURFER_HOME/bin/aparcstats2table --subjectsfile=$sfile --hemi rh --meas volume --tablefile rh_volume.txt --skip -p aparc.a2009s
$python2_bin $FREESURFER_HOME/bin/aparcstats2table --subjectsfile=$sfile --hemi lh --meas volume --tablefile lh_volume.txt --skip -p aparc.a2009s
$python2_bin $FREESURFER_HOME/bin/aparcstats2table --subjectsfile=$sfile --hemi lh --meas area --tablefile lh_area.txt --skip -p aparc.a2009s
$python2_bin $FREESURFER_HOME/bin/asegstats2table --subjectsfile=$sfile --tablefile subcortical.txt --skip

# If they have the same number of lines, then just combine them using paste:
narea_lh=`cat lh_area.txt | wc -l`
narea_rh=`cat rh_area.txt | wc -l`
nthickness_lh=`cat lh_thickness.txt | wc -l`
nthickness_rh=`cat rh_thickness.txt | wc -l`
nvolume_lh=`cat lh_volume.txt | wc -l`
nvolume_rh=`cat rh_volume.txt | wc -l`
nsubcortical=`cat subcortical.txt | wc -l`

if [[ $narea_lh -eq $narea_rh && $nthickness_lh -eq $nthickness_rh && \
      $nvolume_lh -eq $nvolume_rh && $narea_lh -eq $nthickness_lh && \
      $narea_lh -eq $nvolume_lh && $narea_lh -eq $nsubcortical ]]; then
    echo 'Concatenating outputs to merged_rois.txt';
    paste lh_area.txt rh_area.txt > area.txt
    paste lh_volume.txt rh_volume.txt > volume.txt
    paste lh_thickness.txt rh_thickness.txt > thickness.txt
    paste area.txt volume.txt thickness.txt subcortical.txt > merged_rois.txt
else
    printf '\nNumber of rows differs among result files.\n';
    printf 'Result files not merged.';
    printf 'Please consider using R merge().';
fi
