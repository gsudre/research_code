# Runs the TSa pipeline from DTITK for a single mask id
maskid=$1;

template=/data/NCR_SBRB/software/dti-tk/ixi_aging_template_v3.0/template/ixi_aging_template

echo ${maskid}_tensor.nii > ~/tmp/rm${maskid};
cd /scratch/sudregp/dtitk;
dti_rigid_sn ${template}.nii.gz ~/tmp/rm${maskid} EDS;
dti_affine_sn ${template}.nii.gz ~/tmp/rm${maskid} EDS 1;
echo ${maskid}_tensor_aff.nii.gz > ~/tmp/rm${maskid}_aff;
dti_diffeomorphic_sn ${template}.nii.gz ~/tmp/rm${maskid}_aff \
    ${template}_brain_mask.nii.gz 6 0.002;
dti_warp_to_template_group ~/tmp/rm${maskid} ${template}.nii.gz 2 2 2;
