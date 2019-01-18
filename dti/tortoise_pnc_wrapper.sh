s=$1;

cd /data/NCR_SBRB/pnc/dti
mkdir ${s}
cd ${s}
tar -zxf ../../${s}_1.tar.gz
module load afni
Dimon -infile_prefix "${s}/T1_3DAXIAL/Dicoms/*.dcm" \
    -gert_to3d_prefix t1.nii.gz -gert_create_dataset;
fat_proc_convert_dcm_dwis \
    -indir  "${s}/DTI_35dir/* ${s}/DTI_36dir/*" \
    -prefix dwi
rm -rf ${s}

refset=../fatcat_proc_mni_ref/mni_icbm152_t1_tal_nlin_sym_09a_MSKD_ACPCE.nii.gz
refwt=../fatcat_proc_mni_ref/mni_icbm152_t1_tal_nlin_sym_09a_MSKD_ACPCE_wtell.nii.gz
fat_proc_axialize_anat                       \
    -inset  t1.nii.gz    \
    -prefix t1_ax           \
    -mode_t1w                                \
    -refset  $refset \
    -extra_al_wtmask $refwt             \
    -out_match_ref

@SSwarper -input t1_ax.nii.gz -base MNI152_2009_template_SSW.nii.gz -subid ${s};

3dAutomask -prefix automask.nii anatSS.${s}.nii;

fat_proc_imit2w_from_t1w \
    -inset t1_ax.nii.gz \
    -prefix t2_ax_immi \
    -mask automask.nii
gunzip dwi.nii.gz
gunzip t2_ax_immi.nii.gz

# I got the phase information after using ImportDICOM tool from TORTOISE and checking the .list file
DIFFPREP --dwi dwi.nii --bvecs dwi_rvec.dat --bvals dwi_bval.dat \
    --phase vertical --structural t2_ax_immi.nii --mask_image automask.nii

@GradFlipTest -in_dwi dwi_DMC.nii -in_col_matT dwi_DMC.bmtxt \
    -prefix GradFlipTest_rec.txt

3dresample -master dwi_DMC.nii \
    -prefix automask_in_dwi_grid.nii \
    -input automask.nii

my_flip=`cat GradFlipTest_rec.txt`;
fat_proc_dwi_to_dt \
    -in_dwi       dwi_DMC.nii                    \
    -in_col_matT  dwi_DMC.bmtxt                  \
    -in_struc_res dwi_DMC_structural.nii               \
    -in_ref_orig  dwi_DMC_template.nii          \
    -prefix       dwi_DMC_dt                           \
    -mask automask_in_dwi_grid.nii                                   \
    $my_flip

fat_proc_decmap                                     \
    -in_fa       dt_FA.nii.gz     \
    -in_v1       dt_V1.nii.gz     \
    -prefix      DEC