#!/bin/sh
subj=$1

subj_dir=/mnt/neuro/data_by_maskID/$subj/afni

# This one is based on Joel's latest paipeline (see his e-mail). Afterwards, we still need to regress out first 3 PCs of a combined CSFe/WMe mask (CompCor)
afni_proc.py -subj_id $subj                               \
    -dsets ${subj_dir}/rest+orig.HEAD                          \
    -script $subj_dir/rest.proc.compCor.$subj               \
    -copy_anat $subj_dir/mprage+orig       \
    -out_dir $subj_dir/$subj.rest.compCor.results               \
    -blocks despike tshift align tlrc volreg blur mask regress \
    -tcat_remove_first_trs 3                \
    -tlrc_NL_warp                   \
    -anat_uniform_method unifize    \
    -volreg_tlrc_warp               \
    -volreg_align_e2a                                   \
    -mask_segment_anat yes                              \
    -regress_censor_motion 0.2                          \
    -regress_censor_outliers 0.1                        \
    -regress_apply_mot_types demean deriv               \
    -regress_anaticor                                   \
    -regress_anaticor_radius 25                         \
    -regress_run_clustsim yes                            \
    -regress_est_blur_errts                                
tcsh -xef $subj_dir/rest.proc.compCor.$subj | tee $subj_dir/output.rest.compCor.proc.$subj
