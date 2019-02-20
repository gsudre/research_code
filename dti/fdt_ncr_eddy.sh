# After conversion from DCM to nii using convert_ncr_to_nii.sh, use this script
# to create brain mask, QC, and run eddy

module load CUDA/7.5
module load fsl
module load afni

cd $1;

# FSL takes bvecs in the 3 x volumes format
fslroi dwi_comb b0 0 1
bet b0 b0_brain -m -f 0.2

# make QC images for brain mask
@chauffeur_afni                             \
    -ulay  dwi_comb.nii.gz[0]                         \
    -olay  b0_brain_mask.nii.gz                        \
    -opacity 4                              \
    -prefix   QC/brain_mask              \
    -montx 6 -monty 6                       \
    -set_xhairs OFF                         \
    -label_mode 1 -label_size 3             \
    -do_clean

nvol=`cat dwi_comb_cvec.dat | wc -l`;
idx=''; for i in `seq 1 $nvol`; do 
    a=$a' '1;
done;
echo $a > index.txt

# according to the edyd webpage it doesn't matter what we have for acquisition
# parameters.
# https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy/Faq#How_do_I_know_what_to_put_into_my_--acqp_file
# So, let's stick with the same stuff we used for PNC. But actually, the JSON
# coming from our data is quite similar to the PNC one, so I'm not too worried
# about this.
echo "0 -1 0 0.102" > acqparams.txt

# eddy_openmp --imain=dwi --mask=b0_brain_mask --index=index.txt \
#     --acqp=acqparams.txt --bvecs=dwi_cvec.dat --bvals=dwi_bval.dat \
#     --fwhm=0 --flm=quadratic --out=eddy_unwarped_images --cnr_maps --repol --mporder=6

nslices=`fslinfo dwi_comb.nii.gz | grep -e "^dim3" | awk '{ print $2 }'`;
let nslices=$nslices-1;  # make it zero based
seq 1 2 $nslices > my_slspec.txt;
seq 0 2 $nslices >> my_slspec.txt;

eddy_cuda --imain=dwi_comb --acqp=acqparams.txt --index=index.txt \
    --mask=b0_brain_mask --bvals=dwi_comb_bval.dat --bvecs=dwi_comb_rvec.dat \
    --out=eddy_s2v_unwarped_images --niter=8 --fwhm=10,6,4,2,0,0,0,0 \
    --repol --ol_type=both --mporder=8 --s2v_niter=8 \
    --slspec=my_slspec.txt --cnr_maps

