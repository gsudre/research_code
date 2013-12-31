#!/bin/sh
echo "Enter the subject mask ID (4 digits), followed by [ENTER]:"
read subj

subj_dir=/Volumes/neuro/data_by_maskID/$subj/afni
stim_dir=/Volumeso/MR_behavioral/stim_files_analysis1

# start by running Joel's afni_proc, but we do regress out censor
# outliers because for now we're dealing with adults. Also, we
# don't have dummy scans, so no need to remove TRs
afni_proc.py -subj_id $subj     \
    -dsets ${subj_dir}/rest+orig.HEAD                          \
    -script ${subj_dir}/rest.proc.withPhysio.$subj               \
    -copy_anat $subj_dir/mprage+orig                           \
    -out_dir $subj_dir/$subj.restWithPhysio.results \
    -blocks despike align tlrc volreg blur mask regress \
    -volreg_align_e2a                                          \
    -volreg_tlrc_warp                                          \
    -regress_anaticor                                          \
    -regress_censor_motion 0.3                                 \
    -regress_censor_outliers 0.1                               \
    -regress_bandpass 0.01 0.1                                 \
    -regress_apply_mot_types demean deriv                      \
    -regress_run_clustsim no                                   \
    -regress_est_blur_errts

tcsh -xef $subj_dir/rest.proc.withPhysio.$subj | tee $subj_dir/output.rest.withPhysio.proc.$subj

# Now we do the same as above, but including the regressors for physiological
# data
afni_proc.py -subj_id $subj     \
    -dsets ${subj_dir}/rest+orig.HEAD                          \
    -script ${subj_dir}/rest.proc.regressingOutPhysio.$subj               \
    -copy_anat $subj_dir/mprage+orig       \
    -out_dir $subj_dir/$subj.regressingOutPhysio.results                     \
    -blocks despike ricor align tlrc volreg blur mask regress \
    -volreg_align_e2a                                          \
    -volreg_tlrc_warp                                          \
    -regress_anaticor                                          \
    -regress_censor_motion 0.3                                 \
    -regress_censor_outliers 0.1                               \
    -regress_bandpass 0.01 0.1                                 \
    -regress_apply_mot_types demean deriv                      \
    -regress_run_clustsim no                                   \
    -regress_est_blur_errts                                     \
    -ricor_regs ${subj_dir}/oba.slibase.1D                      

tcsh -xef $subj_dir/rest.proc.regressingOutPhysio.$subj | tee $subj_dir/output.rest.regressingOutPhysio.proc.$subj

# Finally, we try Steve's approach, regressing out white matter and ventricles
afni_proc.py -subj_id $subj                               \
    -dsets ${subj_dir}/rest+orig.HEAD                          \
    -script ${subj_dir}/rest.proc.whiteMatterCSF.$subj               \
    -copy_anat $subj_dir/mprage+orig       \
    -out_dir $subj_dir/$subj.whiteMatterCSF.results                        \
    -blocks despike ricor align tlrc volreg blur mask regress \
    -volreg_align_e2a                                   \
    -volreg_tlrc_warp                                   \
    -mask_segment_anat yes                              \
    -regress_censor_motion 0.3                          \
    -regress_censor_outliers 0.1                        \
    -regress_bandpass 0.01 0.1                          \
    -regress_apply_mot_types demean deriv               \
    -regress_ROI WMe CSFe                               \
    -regress_run_clustsim no                            \
    -regress_est_blur_errts                             \
    -ricor_regs ${subj_dir}/oba.slibase.1D                      

tcsh -xef $subj_dir/rest.proc.whiteMatterCSF.$subj | tee $subj_dir/output.rest.whiteMatterCSF.proc.$subj
