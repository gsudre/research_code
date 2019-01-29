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
    --mask=b0_brain_mask --bvals=dwi_bval.dat --bvecs=dwi_cvec.dat \
    --out=eddy_s2v_unwarped_images --niter=8 --fwhm=10,6,4,2,0,0,0,0 \
    --repol --ol_type=both --mporder=8 --s2v_niter=8 \
    --slspec=my_slspec.txt --cnr_maps

dtifit --data=eddy_s2v_unwarped_images --mask=b0_brain_mask \
    --bvals=dwi_bval.dat --bvecs=dwi_cvec.dat --sse --out=dti
