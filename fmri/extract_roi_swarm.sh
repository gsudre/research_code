# Wrapper function for swarm to extract roi for multiple subjects
#
# GS, 08/2017
s=$1
cd /lscratch/$SLURM_JOB_ID
cp /scratch/sudregp/rsfmri/*${s}* .
for seg in aparc aparc.a2009s; do
	if [[ $seg == 'aparc' ]]; then
		rois=115;
	else
		rois=197;
	fi;
	3dresample -inset ${s}_${seg}.nii.gz -prefix seg_in_epi_grid.nii -master errts.${s}.fanaticor+orig -rmode NN -overwrite;
	for r in $(seq 1 $rois); do
    		3dcalc -a seg_in_epi_grid.nii -expr "amongst(a,$r)" -prefix mymask.nii -overwrite;
    		3dmaskave -q -mask mymask.nii errts.${s}.fanaticor+orig > ${r}.1D;
	done;
	res_dir=/scratch/sudregp/rsfmri/$seg/$s
	rm -rf $res_dir
	mkdir $res_dir
	mv *1D $res_dir
done
