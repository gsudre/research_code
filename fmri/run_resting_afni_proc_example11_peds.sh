#!/bin/sh
subj=$1

# subj_dir=/mnt/shaw/data_by_maskID/$subj/afni
# freesurfer_dir=/mnt/shaw/freesurfer5.3_subjects/$subj
subj_dir=~/data/fmri/$subj
freesurfer_dir=~/data/MEG_structural/freesurfer/$subj

# This one is based on AFNI's current example 11 (09092015), copied below

# first, prepare the files we'll need from Freesurfer
mri_convert ${freesurfer_dir}/mri/aparc+aseg.mgz $subj_dir/aparc.a2009s+aseg.nii
3dcalc -a $subj_dir/aparc.a2009s+aseg.nii -expr 'equals(a,4)+equals(a,43)' -prefix $subj_dir/FT_vent.nii
mri_convert ${freesurfer_dir}/mri/wm.seg.mgz $subj_dir/wm.seg.nii
3dcalc -a $subj_dir/wm.seg.nii -prefix $subj_dir/FT_white.nii -expr 'step(a)'

afni_proc.py -subj_id $subj                             \
      -blocks despike tshift align tlrc volreg blur mask regress \
      -copy_anat $subj_dir/mprage+orig                                    \
      -out_dir $subj_dir/$subj.rest.example11_HaskinsPeds.results               \
      -script $subj_dir/rest.proc.example11_HaskinsPeds.$subj               \
      -anat_follower_ROI aaseg anat $subj_dir/aparc.a2009s+aseg.nii   \
      -anat_follower_ROI aeseg epi  $subj_dir/aparc.a2009s+aseg.nii   \
      -anat_follower_ROI FSvent epi $subj_dir/FT_vent.nii                  \
      -anat_follower_ROI FSWe epi $subj_dir/FT_white.nii                   \
      -anat_follower_erode FSvent FSWe                           \
      -dsets ${subj_dir}/rest*+orig.HEAD                         \
      -tcat_remove_first_trs 3                                   \
      -tlrc_base HaskinsPeds_NL_template1.0+tlrc                               \
      -tlrc_NL_warp                                              \
      -volreg_align_e2a                                          \
      -volreg_tlrc_warp                                          \
      -regress_ROI_PC FSvent 3                                   \
      -regress_ROI FSWe                                          \
      -regress_make_corr_vols aeseg FSvent                       \
      -regress_anaticor_fast                                     \
      -regress_anaticor_label FSWe                               \
      -regress_censor_motion 0.2                                 \
      -regress_censor_outliers 0.1                               \
      -regress_apply_mot_types demean deriv                      \
      -regress_est_blur_errts                                    \
      -regress_run_clustsim no
tcsh -xef $subj_dir/rest.proc.example11_HaskinsPeds.$subj 2>&1 | tee $subj_dir/output.rest.example11_HaskinsPeds.proc.$subj

# Example 11. Resting state analysis (now even more modern :).
           
#          o Yes, censor (outliers and motion) and despike.
#          o Use non-linear registration to MNI template.
#          o No bandpassing.
#          o Use fast ANATICOR method (slightly different from default ANATICOR).
#          o Use FreeSurfer segmentation for:
#              - regression of average eroded white matter
#              - regression of first 3 principal components of lateral ventricles
#              - ANATICOR white matter mask
#          o Erode FS white matter and ventricle masks before application.
#          o Bring along FreeSurfer parcellation datasets:
#              - aaseg : NN interpolated onto the anatomical grid
#              - aeseg : NN interpolated onto the EPI        grid
#            These follower datasets are just for evaluation.
#          o Compute average correlation volumes of the errts against the
#            the gray matter (aeseg) and ventricle (FSVent) masks.

        # afni_proc.py -subj_id FT.11.rest                             \
        #   -blocks despike tshift align tlrc volreg blur mask regress \
        #   -copy_anat FT_anat+orig                                    \
        #   -anat_follower_ROI aaseg anat aparc.a2009s+aseg_rank.nii   \
        #   -anat_follower_ROI aeseg epi  aparc.a2009s+aseg_rank.nii   \
        #   -anat_follower_ROI FSvent epi FT_vent.nii                  \
        #   -anat_follower_ROI FSWe epi FT_white.nii                   \
        #   -anat_follower_erode FSvent FSWe                           \
        #   -dsets FT_epi_r?+orig.HEAD                                 \
        #   -tcat_remove_first_trs 2                                   \
        #   -tlrc_base MNI_caez_N27+tlrc                               \
        #   -tlrc_NL_warp                                              \
        #   -volreg_align_e2a                                          \
        #   -volreg_tlrc_warp                                          \
        #   -regress_ROI_PC FSvent 3                                   \
        #   -regress_ROI FSWe                                          \
        #   -regress_make_corr_vols aeseg FSvent                       \
        #   -regress_anaticor_fast                                     \
        #   -regress_anaticor_label FSWe                               \
        #   -regress_censor_motion 0.2                                 \
        #   -regress_censor_outliers 0.1                               \
        #   -regress_apply_mot_types demean deriv                      \
        #   -regress_est_blur_errts                                    \
        #   -regress_run_clustsim no