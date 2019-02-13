s=$1;

cd /data/NCR_SBRB/pnc/dti_fdt
mkdir ${s}
cd ${s}
tar -zxf ../../${s}_1.tar.gz
module load CUDA/7.5
module load fsl
module load afni

# just to produce the .nii files
fat_proc_convert_dcm_dwis \
    -indir  "${s}/DTI_35dir/* ${s}/DTI_36dir/*" \
    -prefix dwi
rm -rf ${s}

# FSL takes bvecs in the 3 x volumes format
fslroi dwi b0 0 1
bet b0 b0_brain -m -f 0.2
idx=''; for i in {1..71}; do 
    a=$a' '1;
done;
echo $a > index.txt
echo "0 -1 0 0.102" > acqparams.txt

# eddy_openmp --imain=dwi --mask=b0_brain_mask --index=index.txt \
#     --acqp=acqparams.txt --bvecs=dwi_cvec.dat --bvals=dwi_bval.dat \
#     --fwhm=0 --flm=quadratic --out=eddy_unwarped_images --cnr_maps --repol --mporder=6

cp ../my_slspec.txt ./
eddy_cuda --imain=dwi --acqp=acqparams.txt --index=index.txt \
    --mask=b0_brain_mask --bvals=dwi_bval.dat --bvecs=dwi_rvec.dat \
    --out=eddy_s2v_unwarped_images --niter=8 --fwhm=10,6,4,2,0,0,0,0 \
    --repol --ol_type=both --mporder=8 --s2v_niter=8 \
    --slspec=my_slspec.txt --cnr_maps

dtifit --data=eddy_s2v_unwarped_images --mask=b0_brain_mask \
    --bvals=dwi_bval.dat --bvecs=eddy_s2v_unwarped_images.eddy_rotated_bvecs \
    --sse --out=dti

# make QC images for brain mask
@chauffeur_afni                             \
    -ulay  dwi.nii.gz[0]                         \
    -olay  b0_brain_mask.nii.gz                        \
    -opacity 4                              \
    -prefix   QC/brain_mask              \
    -montx 6 -monty 6                       \
    -set_xhairs OFF                         \
    -label_mode 1 -label_size 3             \
    -do_clean

# let's take the FA map to the standard space recommended for FSL
# https://fsl.fmrib.ox.ac.uk/fslcourse/lectures/practicals/fdt1/index.html
# first step is just some eroading of all images

# eroding FA image
tbss_1_preproc dti_FA.nii.gz

# make directionality encoded QC pictures, checking that eroded FA looks fine
cd FA
fat_proc_decmap -in_fa dti_FA_FA.nii.gz -in_v1 ../dti_V1.nii.gz \
    -mask ../b0_brain_mask.nii.gz -prefix ../DEC -qc_prefix ../QC/DEC

# transform and apply the transformation to FMRIB58, similar to tbss_2, but we
# actually apply it here
cd FA
fsl_reg dti_FA_FA.nii.gz $FSLDIR/data/standard/FMRIB58_FA_1mm FA_in_FMRIB58_FA_1mm -FA

# apply FA transform to other interesting maps... code copied from tbss_non_fa
for f in L1 L2 L3 MD MO; do
    echo Warping $f;
    applywarp -i ../dti_${f} -o ${f}_FMRIB58_FA_1mm \
        -r $FSLDIR/data/standard/FMRIB58_FA_1mm -w FA_in_FMRIB58_FA_1mm_warp
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
    -prefix   ../QC/FA_transform              \
    -montx 3 -monty 3                       \
    -set_xhairs OFF                         \
    -label_mode 1 -label_size 3             \
    -do_clean

# make QC images for standard errors. Here we set our color scale to have 95th
# percentile of all errors. Meaning, more red = bigger error.
@chauffeur_afni                             \
    -ulay  dwi.nii.gz                       \
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

# for our pipeline, it's worth it to go to DTI-TK space as well, so this way we
# have tensors in the DTI-TK space and also in the FMRIB58 space. However,
# unlike what we did in the past, we don't go to the aging template first; we
# have two separate pipelines, each going from subject space to FMRIB58 or aging
# template. We can do the 13 DTITK tracts in one pipeline, and voxelwise/FSL
# tracts in the other.