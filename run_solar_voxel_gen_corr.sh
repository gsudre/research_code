# we have to create separate solar directories, so the SOLAR residual files don't get overwritten as we run multiple voxels in parallel
# SLURM_JOBID=0
# mkdir /lscratch/${SLURM_JOBID}
net=$1
prop=$2
v=$3
tmp_dir=~/data/tmp/
solar_dir=~/data/solar_paper_v2/
vox=`printf "%05d" $v`
while read tract; do
    target=${net}_${prop}_${tract}
    final_dir=${tmp_dir}/${target}
    if [ ! -d $final_dir ]; then
        mkdir $final_dir
    fi;
    mkdir /lscratch/${SLURM_JOBID}/${target}
    mkdir /lscratch/${SLURM_JOBID}/${target}/${vox}
    cp ${solar_dir}/pedigree.csv ${solar_dir}/procs.tcl ${solar_dir}/both_net${net}_dtiMeanCleaned.csv /lscratch/${SLURM_JOBID}/${target}/${vox}/
    cd /lscratch/${SLURM_JOBID}/${target}/${vox}/
    solar voxel_gen_corr $net $prop $tract $v
    mv /lscratch/${SLURM_JOBID}/${target}/${vox}/results/polygenic.out ${final_dir}/v${vox}_polygenic.out
    rm -rf /lscratch/${SLURM_JOBID}/${target}/${vox}
done < ${solar_dir}/tracts.txt
