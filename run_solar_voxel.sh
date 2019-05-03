# we have to create separate solar directories, so the SOLAR residual files don't get overwritten as we run multiple voxels in parallel
phen_file=$1
v=$2
tmp_dir=~/data/tmp/
solar_dir=~/data/heritability_change/
vox=`printf "%05d" $v`
mkdir ${tmp_dir}/${phen_file}
mkdir /lscratch/${SLURM_JOBID}/${phen_file}
mkdir /lscratch/${SLURM_JOBID}/${phen_file}/${vox}
cp ${solar_dir}/pedigree.csv ${solar_dir}/procs.tcl /lscratch/${SLURM_JOBID}/${phen_file}/${vox}/
sed "s/NA//g" ${solar_dir}/${phen_file}.csv > /lscratch/${SLURM_JOBID}/${phen_file}/${vox}/${phen_file}.csv;
cd /lscratch/${SLURM_JOBID}/${phen_file}/${vox}/
solar run_phen_var $phen_file $vox
mv /lscratch/${SLURM_JOBID}/${phen_file}/${vox}/i_v${v}/polygenic.out ${tmp_dir}/${phen_file}/v${vox}_polygenic.out
rm -rf /lscratch/${SLURM_JOBID}/${phen_file}/${vox}
