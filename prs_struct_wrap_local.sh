# runs PRS voxelwise structural locally, then copies over compiled files
hemi=$1
x=$2
y=$3

module load R
cd /lscratch/$SLURM_JOBID

# for i in {1..163842}; do v=`printf v%06d $i`; echo $v >> voxel_list.txt; done
cp /data/${USER}/prs/voxel_list_struct.txt ./voxel_list.txt

cp /scratch/${USER}/prs/struct_prs_05232018.csv .
cp /scratch/${USER}/prs/struct301.txt .
cp /scratch/${USER}/prs/${hemi}.volume_residuals_301.10.gzip .
split -l 2926 voxel_list.txt  # adapted to 56 cores!

for f in `ls x*`; do
    Rscript --vanilla ~/research_code/prs_struct_voxelwise_local.R \
        /lscratch/${SLURM_JOBID}/$f lscratch ${hemi} $x $y &
done

# wait until all background jobs are complete
wait

cd /lscratch/${SLURM_JOBID}/struct_voxels_*/*/*

cat v*.csv | awk 'NR % 2 == 0' > all_res.csv  # keep only the result lines
cut -d"," -f 2 all_res.csv > total_betas.txt;
cut -d"," -f 3 all_res.csv > total_pvals.txt;
cut -d"," -f 4 all_res.csv > acme_betas.txt;
cut -d"," -f 5 all_res.csv > acme_pvals.txt;
cut -d"," -f 6 all_res.csv > ade_betas.txt;
cut -d"," -f 7 all_res.csv > ade_pvals.txt;

# let's construct a collection script from scratch. R assumes wd is where we start it
echo 'a = read.table("acme_pvals.txt")[,1]
write.table(1-a, file="acme_pvals.txt",row.names=F,col.names=F)
a = read.table("total_pvals.txt")[,1]
write.table(1-a, file="total_pvals.txt",row.names=F,col.names=F)
a = read.table("ade_pvals.txt")[,1]
write.table(1-a,file="ade_pvals.txt",row.names=F,col.names=F)' >> /lscratch/${SLURM_JOBID}/myscript.R

Rscript --vanilla /lscratch/${SLURM_JOBID}/myscript.R

# combine and copy everything
tar -zcvf struct_voxels_301_residuals_${hemi}_${x}_${y}.tar.gz *pvals* *betas*;

cp struct_voxels_301_residuals_${hemi}_${x}_${y}.tar.gz /scratch/${USER}/prs/
