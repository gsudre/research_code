#!/bin/sh
# modified from AFNI Example 11 (below) to do everything in subject space
subj=$1

subj_dir=/scratch/sudregp/rsfmri/$subj
freesurfer_dir=/data/NCR_SBRB/freesurfer5.3_subjects/$subj
SUMA_dir=/data/NCR_SBRB/freesurfer5.3_subjects/$subj/SUMA

# This one is based on AFNI's current example 11 (10/28/2016), copied below

# first, prepare the files we'll need from Freesurfer
cd $subj_dir
@SUMA_Make_Spec_FS -sid $subj -NIFTI -fspath $freesurfer_dir
3dcalc -a ${SUMA_dir}/aparc+aseg.nii -datum byte -prefix FT_vent.nii \
    -expr 'amongst(a,4,43)'
3dcalc -a ${SUMA_dir}/aparc+aseg.nii -datum byte -prefix FT_WM.nii \
    -expr 'amongst(a,2,7,41,46,251,252,253,254,255)'

afni_proc.py -subj_id $subj                             \
      -blocks despike tshift align volreg blur mask regress \
      -copy_anat ${SUMA_dir}/${subj}_SurfVol.nii                                    \
      -out_dir $subj_dir/$subj.rest.subjectSpace.results               \
      -script $subj_dir/rest.proc.subjectSpace.$subj               \
      -anat_follower_ROI aaseg anat ${SUMA_dir}/aparc.a2009s+aseg.nii   \
      -anat_follower_ROI aeseg epi  ${SUMA_dir}/aparc.a2009s+aseg.nii   \
      -anat_follower_ROI FSvent epi ${subj_dir}/FT_vent.nii                  \
      -anat_follower_ROI FSWe epi ${subj_dir}/FT_WM.nii                   \
      -anat_follower_erode FSvent FSWe                           \
      -dsets ${subj_dir}/rest*+orig.HEAD                         \
      -tcat_remove_first_trs 3                                   \
      -volreg_align_to MIN_OUTLIER                               \
      -volreg_align_e2a                                          \
      -regress_ROI_PC FSvent 3                                   \
      -regress_make_corr_vols aeseg FSvent                       \
      -regress_anaticor_fast                                     \
      -regress_anaticor_label FSWe                               \
      -regress_censor_motion 0.2                                 \
      -regress_censor_outliers 0.1                               \
      -regress_apply_mot_types demean deriv                      \
      -regress_est_blur_epits                                    \
      -regress_est_blur_errts                                    \
      -regress_run_clustsim no

#       -align_opts_aea -big_move \

tcsh -xef $subj_dir/rest.proc.subjectSpace.$subj 2>&1 | tee \
    $subj_dir/output.rest.subjectSpace.proc.$subj

# Example 11. Resting state analysis (now even more modern :).
#          o Yes, censor (outliers and motion) and despike.
#          o Register EPI volumes to the one which has the minimum outlier
#               fraction (so hopefully the least motion).
#          o Use non-linear registration to MNI template.
#            * This adds a lot of processing time.
#          o No bandpassing.
#          o Use fast ANATICOR method (slightly different from default ANATICOR).
#          o Use FreeSurfer segmentation for:
#              - regression of first 3 principal components of lateral ventricles
#              - ANATICOR white matter mask (for local white matter regression)
#            * For details on how these masks were created, see "FREESURFER NOTE"
#              in the help, as it refers to this "Example 11".
#          o Input anat is from FreeSurfer (meaning it is aligned with FS masks).
#              - output from FS is usually not quite aligned with input
#          o Erode FS white matter and ventricle masks before application.
#          o Bring along FreeSurfer parcellation datasets:
#              - aaseg : NN interpolated onto the anatomical grid
#              - aeseg : NN interpolated onto the EPI        grid
#            * These 'aseg' follower datasets are just for visualization,
#              they are not actually required for the analysis.
#          o Compute average correlation volumes of the errts against the
#            the gray matter (aeseg) and ventricle (FSVent) masks.

#            Note: it might be reasonable to use either set of blur estimates
#                  here (from epits or errts).  The epits (uncleaned) dataset
#                  has all of the noise (though what should be considered noise
#                  in this context is not clear), while the errts is motion
#                  censored.  For consistency in resting state, it would be
#                  reasonable to stick with epits.  They will likely be almost
#                  identical.


#                 afni_proc.py -subj_id FT.11.rest                             \
#                   -blocks despike tshift align tlrc volreg blur mask regress \
#                   -copy_anat FT_SurfVol.nii                                  \
#                   -anat_follower_ROI aaseg anat aparc.a2009s+aseg.nii        \
#                   -anat_follower_ROI aeseg epi  aparc.a2009s+aseg.nii        \
#                   -anat_follower_ROI FSvent epi FT_vent.nii                  \
#                   -anat_follower_ROI FSWe epi FT_white.nii                   \
#                   -anat_follower_erode FSvent FSWe                           \
#                   -dsets FT_epi_r?+orig.HEAD                                 \
#                   -tcat_remove_first_trs 2                                   \
#                   -tlrc_base MNI_caez_N27+tlrc                               \
#                   -tlrc_NL_warp                                              \
#                   -volreg_align_to MIN_OUTLIER                               \
#                   -volreg_align_e2a                                          \
#                   -volreg_tlrc_warp                                          \
#                   -regress_ROI_PC FSvent 3                                   \
#                   -regress_make_corr_vols aeseg FSvent                       \
#                   -regress_anaticor_fast                                     \
#                   -regress_anaticor_label FSWe                               \
#                   -regress_censor_motion 0.2                                 \
#                   -regress_censor_outliers 0.1                               \
#                   -regress_apply_mot_types demean deriv                      \
#                   -regress_est_blur_epits                                    \
#                   -regress_est_blur_errts                                    \
#                   -regress_run_clustsim no
