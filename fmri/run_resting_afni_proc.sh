#!/bin/sh
subj=$1

subj_dir=/mnt/neuro/data_by_maskID/$subj/afni

# # start by running Joel's afni_proc, but we do regress out censor
# # outliers because for now we're dealing with adults, and reduce
# # motion threshold accordingly
# afni_proc.py -subj_id $subj     \
#     -dsets ${subj_dir}/rest+orig.HEAD                          \
#     -script ${subj_dir}/rest.proc.withPhysio.$subj               \
#     -copy_anat $subj_dir/mprage+orig                           \
#     -out_dir $subj_dir/$subj.rest.withPhysio.results \
#     -blocks despike tshift align tlrc volreg blur mask regress \
#     -tcat_remove_first_trs 3                \
#     -volreg_align_e2a                                          \
#     -volreg_tlrc_warp                                          \
#     -regress_anaticor                                          \
#     -regress_censor_motion 0.2                                 \
#     -regress_censor_outliers 0.1                               \
#     -regress_bandpass 0.01 0.1                                 \
#     -regress_apply_mot_types demean deriv                      \
#     -regress_run_clustsim no                                   \
#     -regress_est_blur_errts
# tcsh -xef $subj_dir/rest.proc.withPhysio.$subj | tee $subj_dir/output.rest.withPhysio.proc.$subj

# Now we do the same as above, but including the regressors for physiological
# data
afni_proc.py -subj_id $subj     \
    -dsets ${subj_dir}/rest+orig.HEAD                          \
    -script ${subj_dir}/rest.proc.regressingOutPhysio.$subj               \
    -copy_anat $subj_dir/mprage+orig       \
    -out_dir $subj_dir/$subj.rest.regressingOutPhysio.results                     \
    -blocks despike tshift ricor align tlrc volreg blur mask regress \
    -tcat_remove_first_trs 3                \
    -ricor_regs_nfirst 3                    \
    -volreg_align_e2a                                          \
    -volreg_tlrc_warp                                          \
    -regress_anaticor                                          \
    -regress_censor_motion 0.2                                 \
    -regress_censor_outliers 0.1                               \
    -regress_bandpass 0.01 0.1                                 \
    -regress_apply_mot_types demean deriv                      \
    -regress_run_clustsim no                                   \
    -regress_est_blur_errts                                     \
    -ricor_regs ${subj_dir}/oba.slibase.1D                      
tcsh -xef $subj_dir/rest.proc.regressingOutPhysio.$subj | tee $subj_dir/output.rest.regressingOutPhysio.proc.$subj

# # Finally, we try Steve's approach, regressing out white matter and ventricles.
# afni_proc.py -subj_id $subj                               \
#     -dsets ${subj_dir}/rest+orig.HEAD                          \
#     -script ${subj_dir}/rest.proc.whiteMatterCSF.$subj               \
#     -copy_anat $subj_dir/mprage+orig       \
#     -out_dir $subj_dir/$subj.rest.whiteMatterCSF.results               \
#     -blocks despike tshift ricor align tlrc volreg blur mask regress \
#     -tcat_remove_first_trs 3                \
#     -ricor_regs_nfirst 3                    \
#     -volreg_align_e2a                                   \
#     -volreg_tlrc_warp                                   \
#     -mask_segment_anat yes                              \
#     -regress_censor_motion 0.2                          \
#     -regress_censor_outliers 0.1                        \
#     -regress_bandpass 0.01 0.1                          \
#     -regress_apply_mot_types demean deriv               \
#     -regress_ROI WMe CSFe                               \
#     -regress_run_clustsim no                            \
#     -regress_est_blur_errts                             \
#     -ricor_regs ${subj_dir}/oba.slibase.1D                      
# tcsh -xef $subj_dir/rest.proc.whiteMatterCSF.$subj | tee $subj_dir/output.rest.whiteMatterCSF.proc.$subj

# # Sometimes Steve's approach doesn't work because we couldn't create physio regressors. In those cases, run the same as above without regressing out physio
# afni_proc.py -subj_id $subj                               \
#     -dsets ${subj_dir}/rest+orig.HEAD                          \
#     -script ${subj_dir}/rest.proc.whiteMatterCSFwithPhysio.$subj               \
#     -copy_anat $subj_dir/mprage+orig       \
#     -out_dir $subj_dir/$subj.rest.whiteMatterCSFwithPhysio.results               \
#     -blocks despike tshift align tlrc volreg blur mask regress \
#     -tcat_remove_first_trs 3                \
#     -volreg_align_e2a                                   \
#     -volreg_tlrc_warp                                   \
#     -mask_segment_anat yes                              \
#     -regress_censor_motion 0.2                          \
#     -regress_censor_outliers 0.1                        \
#     -regress_bandpass 0.01 0.1                          \
#     -regress_apply_mot_types demean deriv               \
#     -regress_ROI WMe CSFe                               \
#     -regress_run_clustsim no                            \
#     -regress_est_blur_errts                                
# tcsh -xef $subj_dir/rest.proc.whiteMatterCSFwithPhysio.$subj | tee $subj_dir/output.rest.whiteMatterCSFwithPhysio.proc.$subj

