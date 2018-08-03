# Runs FATCAT using ROI labels from Freesurfer pipeline, on exported TORTOISe data

# where all subject directories reside
data_dir=$1
subj=$2

mkdir ${data_dir}/${subj}/fatcat;
cd ${data_dir}/${subj}/fatcat;

proc_dir=${data_dir}/${subj}/exported/

# Guess the axis flip to use
\@GradFlipTest -in_dwi ${proc_dir}/${subj}.nii \
    -in_col_matT ${proc_dir}/${subj}.bmtxt \
    -prefix GradFlipTest_rec.txt;

# for the actual tract estimation using uncertainties:
myflip=`cat GradFlipTest_rec.txt`;
fat_proc_dwi_to_dt -in_dwi ${proc_dir}/${subj}.nii \
    -in_col_matT ${proc_dir}/${subj}.bmtxt \
    -prefix dwi \
    -in_struc_res ${proc_dir}/edti_DMCstructural.nii \
    -in_ref_orig ${proc_dir}/edti_DMCtemplate.nii \
    -mask_from_struc $myflip;

# for further QC of the results:
fat_proc_decmap                                     \
    -in_fa       dt_FA.nii.gz     \
    -in_v1      dt_V1.nii.gz     \
    -mask      dwi_mask.nii.gz  \
    -prefix      DEC

# # time to bring in the Freesurfer parcellations to the DWI space:
# suma_dir=${SUBJECTS_DIR}/${subj}/SUMA;
# fat_proc_map_to_dti                                                \
#     -source          $suma_dir/brain.nii             \
#     -followers_NN    $suma_dir/aparc*_REN_*.nii.gz   \
#     -followers_surf  $suma_dir/std.141.*.gii         \
#     -followers_ndset $suma_dir/std.141.*.niml.dset   \
#     -followers_spec  $suma_dir/std.141.*.spec        \
#     -base            ${proc_dir}/${dwi_root}.nii'[0]'         \
#     -prefix          fs

# # selecting our ROIs:
# # list all (= 2, probably) renumbered GM maps
# ren_gm=`ls fs_*_REN_gm.nii.gz`
# wmfa="dt_FA.nii.gz"
# wbmask="MASK.nii"
# for gm_in in $ren_gm; do
#     gm_sel="sel_${gm_in}";
#     # apply the ROI (de)selector
#     3dcalc                                       \
#         -echo_edu                                \
#         -a $gm_in                                \
#         -expr 'a*not(equals(a,2)+equals(a,22))'  \
#         -prefix $gm_sel
#     # keep the labeltables from the original
#     3drefit                                      \
#         -copytables                              \
#         $gm_in                                   \
#         $gm_sel
#     gm_roi=`echo $gm_sel | sed -e "s/.nii.gz//"`
#     # inflate GM ROIs up to (but not overlapping) the FA-WM
#     3dROIMaker                                   \
#         -inset    $gm_sel                        \
#         -refset   $gm_sel                        \
#         -skel_stop_strict                        \
#         -skel_thr 0.2                            \
#         -wm_skel  $wmfa                          \
#         -inflate  1                              \
#         -neigh_upto_vert                         \
#         -mask     $wbmask                        \
#         -prefix   $gm_roi                        \
#         -nifti
# done

# # finally, do the tracking:
# gm_netw=sel_fs_aparc+aseg_REN_gm_GMI.nii.gz
# 3dTrackID                             \
#     -mode PROB                        \
#     -dti_in   dt                      \
#     -netrois  $gm_netw                \
#     -uncert   dt_UNC.nii.gz           \
#     -prefix   o.pr00                  \
#     -nifti                            \
#     -no_indipair_out                  \
#     -dump_rois AFNI                   \
#     -alg_Thresh_FA      0.2           \
#     -alg_Thresh_Frac    0.1           \
#     -alg_Nseed_Vox      5             \
#     -alg_Nmonte      1000             \
#     -echo_edu                         \
#     -overwrite
