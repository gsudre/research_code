# runs one permutation of PRS voxelwise strucutal locally, then copies over compiled files
hemi=$1
perm=`printf %04d $2`
x=$3
y=$4

module load R
cd /lscratch/$SLURM_JOBID

# for i in {1..163842}; do v=`printf v%06d $i`; echo $v >> voxel_list.txt; done
cp /data/${USER}/prs/voxel_list_struct.txt ./voxel_list.txt

cp /scratch/${USER}/prs/struct_updated_clin_and_vol_278_04192018.csv .
cp /scratch/${USER}/prs/maskids_struct_updated_clin_and_vol_278_04192018_3tonly.txt .
cp /scratch/${USER}/prs/${hemi}.volume.10.gzip .
split -l 5121 voxel_list.txt  # adapted to 32 cores!

for f in `ls x*`; do
    Rscript --vanilla ~/research_code/prs_struct_voxelwise_local_perm.R \
        /lscratch/${SLURM_JOBID}/$f lscratch ${hemi} $perm $x $y &
done