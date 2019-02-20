s=$1;

cd /data/NCR_SBRB/pnc/dti_fdt/preproc/${s}

module load fsl
module load afni

# let's do some preparation for TBSS and generate some QC on that, and also the
# outputs from autoPtx

# eroding FA image
tbss_1_preproc dti_FA.nii.gz

ln -s origdata/dti_FA.nii.gz ./
ln -s FA/dti_FA_FA.nii.gz dti_FA_eroded.nii.gz

# make directionality encoded QC pictures, checking that eroded FA looks fine.
# Note that the dtifit results, and the std alignment were run by autoPtx!
fat_proc_decmap -in_fa dti_FA_eroded.nii.gz -in_v1 dti_V1.nii.gz \
    -mask nodif_brain_mask.nii.gz -prefix DEC

# apply the transform calculated by autoPtx to a few maps. code copied from 
# tbss_non_fa
for f in FA L1 L2 L3 MD MO FA_eroded; do
    echo Warping $f;
    applywarp -i dti_${f} -o ${f}_in_FMRIB58_FA_1mm \
        -r $FSLDIR/data/standard/FMRIB58_FA_1mm -w nat2std_warp
done

# make transformation QC figure: warped subject B0 is the overlay!
@chauffeur_afni                             \
    -ulay  $FSLDIR/data/standard/FMRIB58_FA_1mm.nii.gz                     \
    -olay  FA_in_FMRIB58_FA_1mm.nii.gz                         \
    -ulay_range 0% 150%                     \
    -func_range_perc 50                     \
    -pbar_posonly                           \
    -cbar "red_monochrome"                  \
    -opacity 8                              \
    -prefix   QC/FA_transform              \
    -montx 3 -monty 3                       \
    -set_xhairs OFF                         \
    -label_mode 1 -label_size 3             \
    -do_clean

# make QC images for standard errors. Here we set our color scale to have 95th
# percentile of all errors. Meaning, more red = bigger error.
@chauffeur_afni                             \
    -ulay  data.nii.gz                       \
    -olay  dti_sse.nii.gz                          \
    -opacity 5                              \
    -pbar_posonly   \
    -cbar Spectrum:red_to_blue              \
    -set_subbricks 0 0 0     \
    -prefix   QC/sse              \
    -montx 6 -monty 6                       \
    -set_xhairs OFF                         \
    -label_mode 1 -label_size 3             \
    -thr_olay 0 \
    -func_range_perc_nz 95 \
    -do_clean

# we can derive the skeleton later, either based on FMRIB58 or group

# note that we need to look at
# https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/TBSS/UserGuide#Using_non-FA_Images_in_TBSS
# to run the non-FA files!

