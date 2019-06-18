# After conversion from DCM to nii using convert_ncr_to_nii.sh, use this script
# to create brain mask, QC, and run eddy

module load CUDA/7.5
module load fsl/6.0.0
module load afni

cd $1;

if [ -e dwi_clean.nii.gz ]; then
    file_root='dwi_clean';
elif [ -e dwi_cropped.nii.gz ]; then
    file_root='dwi_cropped';
else
    file_root='dwi_comb'
fi

fslreorient2std $file_root dwi_reorient

# our data needs an additional flip, compared to PNC
1dDW_Grad_o_Mat++ -in_row_vec ${file_root}_rvec.dat \
    -out_row_vec bvecs -flip_x

# FSL takes bvecs in the 3 x volumes format
fslroi dwi_reorient b0 0 1
bet b0 b0_brain -m -f 0.2

nvol=`fslinfo dwi_reorient | grep -e "^dim4" | awk '{ print $2 }'`;
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

nslices=`fslinfo dwi_reorient.nii.gz | grep -e "^dim3" | awk '{ print $2 }'`;
let nslices=$nslices-1;  # make it zero based
seq 1 2 $nslices > my_slspec.txt;
seq 0 2 $nslices >> my_slspec.txt;

# note that bypassing the shell check as we're doing here is not kosher, so eddy
# advises double checking the data
eddy_cuda --imain=dwi_reorient --acqp=acqparams.txt --index=index.txt \
    --mask=b0_brain_mask --bvals=${file_root}_bval.dat --bvecs=bvecs \
    --out=eddy_s2v_unwarped_images --niter=8 --fwhm=10,6,4,2,0,0,0,0 \
    --repol --ol_type=both --mporder=8 --s2v_niter=8 \
    --slspec=my_slspec.txt --cnr_maps --data_is_shelled

# copying over some files to their correct names for bedpostX
cp eddy_s2v_unwarped_images.nii.gz data.nii.gz;
cp bvecs old_bvecs
cp ${file_root}_bval.dat bvals;
cp eddy_s2v_unwarped_images.eddy_rotated_bvecs bvecs;
cp b0_brain_mask.nii.gz nodif_brain_mask.nii.gz;
chgrp NCR_SBRB data.nii.gz bvals bvecs nodif_brain_mask.nii.gz;
chmod 770 data.nii.gz bvals bvecs nodif_brain_mask.nii.gz;
