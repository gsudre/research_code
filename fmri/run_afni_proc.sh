#!/bin/sh
echo "Enter the subject mask ID (4 digits), followed by [ENTER]:"
read subj

subj_dir=/mnt/neuro/data_by_maskID/$subj/afni
stim_dir=/mnt/neuro/MR_behavioral/stim_files_analysis1

afni_proc.py -dsets ${subj_dir}/stop_run1+orig.BRIK           \
    ${subj_dir}/stop_run2+orig.BRIK                   \
    ${subj_dir}/stop_run3+orig.BRIK                   \
    ${subj_dir}/stop_run4+orig.BRIK                   \
    -scr_overwrite                              \
    -script $subj_dir/stop.proc.$subj                 \
    -subj_id $subj                                                          \
    -out_dir $subj_dir/$subj.stop.results                     \
    -copy_anat $subj_dir/mprage+orig                   \
    -blocks tshift align tlrc volreg blur mask scale regress        \
    -tshift_align_to -tzero 0                       \
    -volreg_align_e2a                           \
        -volreg_tlrc_warp                           \
    -volreg_align_to last                           \
    -blur_size 8                                \
    -align_opts_aea -cost lpc+zz -AddEdge                   \
    -regress_basis 'BLOCK(1,1)'                     \
    -regress_censor_motion 1                   \
    -regress_est_blur_epits                         \
    -regress_est_blur_errts                         \
    -regress_no_fitts                           \
    -regress_stim_times                         \
        $stim_dir/${subj}_STG-correct.txt       \
        $stim_dir/${subj}_STG-incorrect.txt       \
        $stim_dir/${subj}_STI-correct.txt       \
        $stim_dir/${subj}_STI-incorrect.txt       \
        -regress_stim_labels    STG-correct                \
                STG-incorrect            \
                STI-correct              \
                STI-incorrect             \
    -regress_opts_3dD       -bout                       \
                -tout                       \
                -local_times                    \
                -GOFORIT 99                                     \
                -allzero_OK                                     \
                -jobs 3                                         \
                -noFDR                                          \
    -regress_opts_reml  -GOFORIT 99                 \
    -regress_reml_exec   

tcsh -xef $subj_dir/stop.proc.$subj | tee $subj_dir/output.stop.proc.$subj
# -tcat_remove_first_trs 4                       \