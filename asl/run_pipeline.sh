#!/bin/bash
# Call with aguments maskid, video1, video2, tfree1, tfree2, anat
# where each directory doesn't include asteriscs
# Call it from the directory in which the resulting files will reside

# Converting DICOMs to BRIKs
Dimon -infile_pattern "$2/*.dcm" -gert_to3d_prefix ${1}_scan_4mm_r1 -gert_create_dataset
Dimon -infile_pattern "$3/*.dcm" -gert_to3d_prefix ${1}_scan_4mm_r2 -gert_create_dataset
Dimon -infile_pattern "$4/*.dcm" -gert_to3d_prefix ${1}_scan_4mm_resting_r1 -gert_create_dataset
Dimon -infile_pattern "$5/*.dcm" -gert_to3d_prefix ${1}_scan_4mm_resting_r2 -gert_create_dataset

# Register volumes within scans
3dvolreg -verbose -zpad 1 -base ${1}_scan_4mm_r1+orig'[5]' -1Dfile dfile.vid1.1D -prefix volreg.vid1 -cubic ${1}_scan_4mm_r1+orig
3dvolreg -verbose -zpad 1 -base ${1}_scan_4mm_r2+orig'[5]' -1Dfile dfile.vid2.1D -prefix volreg.vid2 -cubic ${1}_scan_4mm_r2+orig
3dvolreg -verbose -zpad 1 -base ${1}_scan_4mm_r1+orig'[5]' -1Dfile dfile.tfree1.1D -prefix volreg.tfree1 -cubic ${1}_scan_4mm_resting_r1+orig
3dvolreg -verbose -zpad 1 -base ${1}_scan_4mm_r2+orig'[5]' -1Dfile dfile.tfree2.1D -prefix volreg.tfree2 -cubic ${1}_scan_4mm_resting_r2+orig
  
# Convert the anatomical scan
Dimon -infile_pattern "$6/*.dcm" -gert_to3d_prefix anat -gert_create_dataset
@auto_tlrc -base TT_N27+tlrc -input anat+orig

for scan in vid1 vid2 tfree1 tfree2;
do
    # Align all scans to anatomy
    align_epi_anat.py -anat anat+orig -epi volreg.${scan}+orig -epi_base 5 -giant_move -epi2anat -volreg off -tshift off -tlrc_apar anat+tlrc

    # Generate movement plots
    1d_tool.py -infile dfile.${scan}.1D -set_nruns 1 -derivative -collapse_cols euclidean_norm -write motion.${scan}.enorm.1D

    # Plot movement and alignments
    afni anat+orig volreg.${scan}_al+orig
    1dplot -ylabel 'Motion (Euclidean Norm)' -xlabel 'Images' motion.${scan}.enorm.1D

    # run procPCASL script in the original data
    csh ~/research_code/asl/procPCASL.sh volreg.${scan}+orig.BRIK 2500 1500

    # warp final result to tlrc
    3dAllineate -base anat+tlrc -input volreg.${scan}_cbf+orig -1Dmatrix_apply volreg.${scan}_al_tlrc_mat.aff12.1D -prefix volreg.${scan}_cbf+tlrc
done
