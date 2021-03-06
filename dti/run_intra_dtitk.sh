# Runs intra subject analysis for all files in a folder
base_dir=/mnt/neuro/dti_longitudinal/analysis_robust/
mrn=$1
aging_template=${base_dir}/ixi_aging_template.nii.gz

cd ${base_dir}/${mrn}
ls -1 *_tensor.nii > intra_subjs.txt
dti_template_bootstrap ${aging_template} intra_subjs.txt EDS
dti_affine_population mean_initial.nii.gz intra_subjs.txt EDS 3
TVtool -in mean_affine3.nii.gz -tr
BinaryThresholdImageFilter mean_affine3_tr.nii.gz mask.nii.gz 0.01 100 1 0
dti_diffeomorphic_population mean_affine3.nii.gz intra_subjs_aff.txt mask.nii.gz 0.002
dti_warp_to_template_group intra_subjs.txt mean_diffeomorphic_initial6.nii.gz 2 2 2
ls -1 *_tensor_diffeo.nii.gz > intra_subjs_diffeo.txt
TVMean -in intra_subjs_diffeo.txt -out mean_intra_${mrn}.nii.gz
