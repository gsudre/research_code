#!/bin/bash
# Written by Gustavo Sudre, 01/2015. Adapted from Joahanna Darko's script.

subj=0498
subj_dir=~/tmp/${subj}/afni/${subj}.stop.results/
rois=(amygdala)
cond1=STG-correct
cond2=STG-incorrect
cond3=STI-correct
cond4=STI-incorrect

old_pwd=`pwd`
cd $subj_dir

# # first, run the same 3dDeconvolve as before, but inverting the contrasts
# 3dDeconvolve -input pb04.$subj.r*.scale+tlrc.HEAD                        \
#     -censor censor_${subj}_combined_2.1D                                 \
#     -polort 2                                                            \
#     -num_stimts 10                                                       \
#     -stim_times 1 stimuli/0498_STG-correct.txt 'BLOCK(1,1)'              \
#     -stim_label 1 STG-correct                                            \
#     -stim_times 2 stimuli/0498_STG-incorrect.txt 'BLOCK(1,1)'            \
#     -stim_label 2 STG-incorrect                                          \
#     -stim_times 3 stimuli/0498_STI-correct.txt 'BLOCK(1,1)'              \
#     -stim_label 3 STI-correct                                            \
#     -stim_times 4 stimuli/0498_STI-incorrect.txt 'BLOCK(1,1)'            \
#     -stim_label 4 STI-incorrect                                          \
#     -stim_file 5 motion_demean.1D'[0]' -stim_base 5 -stim_label 5 roll   \
#     -stim_file 6 motion_demean.1D'[1]' -stim_base 6 -stim_label 6 pitch  \
#     -stim_file 7 motion_demean.1D'[2]' -stim_base 7 -stim_label 7 yaw    \
#     -stim_file 8 motion_demean.1D'[3]' -stim_base 8 -stim_label 8 dS     \
#     -stim_file 9 motion_demean.1D'[4]' -stim_base 9 -stim_label 9 dL     \
#     -stim_file 10 motion_demean.1D'[5]' -stim_base 10 -stim_label 10 dP  \
#     -bout                                                                \
#     -tout                                                                \
#     -local_times                                                         \
#     -GOFORIT 99                                                          \
#     -allzero_OK                                                          \
#     -jobs 3                                                              \
#     -noFDR                                                               \
#     -gltsym 'SYM: STI-correct -STG-correct' -glt_label 1                 \
#         STI-correct_VS_STG-correct                                       \
#     -gltsym 'SYM: STI-incorrect -STG-correct' -glt_label 2               \
#         STI-incorrect_VS_STG-correct                                     \
#     -gltsym 'SYM: STI-incorrect -STI-correct' -glt_label 3               \
#         STI-incorrect_VS_STI-correct                                     \
#     -fout -tout -x1D X.xmat.inverted.1D -xjpeg X.inverted.jpg            \
#     -x1D_uncensored X.nocensor.xmat.inverted.1D                          \
#     -errts errts.inverted.${subj}                                        \
#     -bucket stats.inverted.${subj}

# then, run the same as above, but using the seeds regressors for each ROI
for roi in ${rois[@]}; do
    echo ==== 3dDeconvolve $roi ====
    3dDeconvolve -input pb04.$subj.r*.scale+tlrc.HEAD                        \
        -censor censor_${subj}_combined_2.1D                                 \
        -polort 2                                                            \
        -num_stimts 14                                                       \
        -stim_times 1 stimuli/${subj}_STG-correct.txt 'BLOCK(1,1)'           \
        -stim_label 1 STG-correct                                            \
        -stim_times 2 stimuli/${subj}_STG-incorrect.txt 'BLOCK(1,1)'         \
        -stim_label 2 STG-incorrect                                          \
        -stim_times 3 stimuli/${subj}_STI-correct.txt 'BLOCK(1,1)'           \
        -stim_label 3 STI-correct                                            \
        -stim_times 4 stimuli/${subj}_STI-incorrect.txt 'BLOCK(1,1)'         \
        -stim_label 4 STI-incorrect                                          \
        -stim_file 5 motion_demean.1D'[0]' -stim_base 5 -stim_label 5 roll   \
        -stim_file 6 motion_demean.1D'[1]' -stim_base 6 -stim_label 6 pitch  \
        -stim_file 7 motion_demean.1D'[2]' -stim_base 7 -stim_label 7 yaw    \
        -stim_file 8 motion_demean.1D'[3]' -stim_base 8 -stim_label 8 dS     \
        -stim_file 9 motion_demean.1D'[4]' -stim_base 9 -stim_label 9 dL     \
        -stim_file 10 motion_demean.1D'[5]' -stim_base 10 -stim_label 10 dP  \
        -stim_file 11 gPPI/$roi.$cond1.rall.PPI.reconv.1D -stim_label 11     \
            $roi.$cond1.PPI                                                  \
        -stim_file 12 gPPI/$roi.$cond2.rall.PPI.reconv.1D -stim_label 12     \
            $roi.$cond2.PPI                                                  \
        -stim_file 13 gPPI/$roi.$cond3.rall.PPI.reconv.1D -stim_label 13     \
            $roi.$cond3.PPI                                                  \
        -stim_file 14 gPPI/$roi.$cond4.rall.PPI.reconv.1D -stim_label 14     \
            $roi.$cond4.PPI                                                  \
        -bout                                                                \
        -tout                                                                \
        -local_times                                                         \
        -GOFORIT 99                                                          \
        -allzero_OK                                                          \
        -jobs 3                                                              \
        -noFDR                                                               \
        -gltsym 'SYM: STI-correct -STG-correct' -glt_label 1                 \
            STI-correct_VS_STG-correct                                       \
        -gltsym 'SYM: STI-incorrect -STG-correct' -glt_label 2               \
            STI-incorrect_VS_STG-correct                                     \
        -gltsym 'SYM: STI-incorrect -STI-correct' -glt_label 3               \
            STI-incorrect_VS_STI-correct                                     \
        -fout -tout -x1D gPPI/X.xmat.inverted.1D -xjpeg gPPI/X.inverted.jpg  \
        -x1D_uncensored gPPI/X.nocensor.xmat.inverted.1D                     \
        -errts gPPI/errts.inverted.$roi.${subj}                              \
        -bucket gPPI/stats.inverted.$roi.${subj}
done

cd $old_pwd