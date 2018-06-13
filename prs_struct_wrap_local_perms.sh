# runs one permutation of PRS voxelwise strucutal locally, then copies over compiled files
hemi=$1
perm=`printf %04d $2`
x=$3
y=$4

module load R
cd /lscratch/$SLURM_JOBID

# for i in {1..163842}; do v=`printf v%06d $i`; echo $v >> voxel_list.txt; done
cp /data/${USER}/prs/voxel_list_struct.txt ./voxel_list.txt

cp /scratch/${USER}/prs/struct_prs_06122018.csv .
cp /scratch/${USER}/prs/struct301.txt .
cp /scratch/${USER}/prs/${hemi}.thickness_residuals_301.10.gzip .
split -l 5121 voxel_list.txt  # adapted to 32 cores!

for f in `ls x*`; do
    Rscript --vanilla ~/research_code/prs_struct_voxelwise_local_perm.R \
        /lscratch/${SLURM_JOBID}/$f lscratch ${hemi} $perm $x $y &
done

# wait until all background jobs are complete
wait

cd /lscratch/${SLURM_JOBID}/struct_voxels_*/*/*/perm*

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
tar -zcvf struct_voxels_${hemi}_${x}_${y}_perm${perm}.tar.gz *pvals* *betas*;

cp struct_voxels_${hemi}_${x}_${y}_perm${perm}.tar.gz /scratch/${USER}/prs/
