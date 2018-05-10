# run different permutations in a local node and copy over the compiled files
dti_mode=$1
perm=`printf %04d $2`
x=$3
y=$4

cd /lscratch/${SLURM_JOBID}
cp /scratch/${USER}/prs/dti_prs_05092018.csv .
cp /scratch/${USER}/prs/dti_${dti_mode}_voxelwise_05092018.RData .
cp /scratch/${USER}/prs/mean_387_fa_skeleton_mask.nii.gz .
for i in {1..12166}; do 
    v=`printf v%05d $i`;
    echo "$v" >> voxel_list;
done

# split voxels into 8 files
split -l 1521 voxel_list
module load R
for f in `ls x*`; do
    Rscript --vanilla ~/research_code/dti/prs_dti_voxelwise_voxelList_perm.R \
        $x $y /lscratch/${SLURM_JOBID}/${f} $perm $dti_mode T &
done

# wait until all background jobs are complete
wait

# wait until we have all voxels
cd /lscratch/${SLURM_JOBID}/dti_voxels_*/*/*/perm*

# let's construct a collection script from scratch. R assumes wd is where we start it
echo 'imuser=Sys.getenv("USER")
p = read.table(sprintf("/scratch/%s/1084_rd.txt", imuser))
acme_b=p
acme_p=p
tot_b=p
tot_p=p
ade_b=p
ade_p=p
for (i in 1:dim(p)[1]) {
    if (i %% 1000 == 0) {print(i)}
    fname = sprintf("v%05d.csv", i)
    d = read.csv(fname)
    acme_p[i, 4] = 1-d$acme_p
    acme_b[i, 4] = d$acme
    tot_p[i, 4] = 1-d$tot_p
    tot_b[i, 4] = d$tot
    ade_p[i, 4] = 1-d$ade_p
    ade_b[i, 4] = d$ade 
}
write.table(acme_p, file="acme_pvals.txt", row.names=F, col.names=F)
write.table(acme_b, file="acme_betas.txt", row.names=F, col.names=F)
write.table(tot_p, file="tot_pvals.txt", row.names=F, col.names=F)
write.table(tot_b, file="tot_betas.txt", row.names=F, col.names=F)
write.table(ade_p, file="ade_pvals.txt", row.names=F, col.names=F)
write.table(ade_b, file="ade_betas.txt", row.names=F, col.names=F)' >> /lscratch/${SLURM_JOBID}/myscript.R

Rscript --vanilla /lscratch/${SLURM_JOBID}/myscript.R

# mass convert compiled files to NIFTI
module load afni
mask=/lscratch/${SLURM_JOBID}/mean_387_fa_skeleton_mask.nii.gz
for r in acme tot ade; do
    cat ${r}_pvals.txt | 3dUndump -master $mask -mask $mask -datum float \
        -prefix ${r}_pvals.nii.gz -overwrite -;
    cat ${r}_betas.txt | 3dUndump -master $mask -mask $mask -datum float \
        -prefix ${r}_betas.nii.gz -overwrite -;
    done;
3dTcat -output dti_${dti_mode}_${x}_${y}_perm${perm}.nii.gz acme_betas.nii.gz acme_pvals.nii.gz \
    tot_betas.nii.gz tot_pvals.nii.gz ade_betas.nii.gz ade_pvals.nii.gz;

cp dti_${dti_mode}_${x}_${y}_perm${perm}.nii.gz /scratch/${USER}/prs/