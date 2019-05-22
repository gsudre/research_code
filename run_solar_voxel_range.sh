# we have to create separate solar directories, so the SOLAR residual files don't get overwritten as we run multiple voxels in parallel
phen_file=$1
v1=$2
v2=$3
tmp_dir=~/data/tmp/
solar_dir=~/data/heritability_change/
mkdir ${tmp_dir}/${phen_file}
mkdir /lscratch/${SLURM_JOBID}/${phen_file}
# making sure we only access the network once
cp ${solar_dir}/pedigree.csv ${solar_dir}/procs.tcl /lscratch/${SLURM_JOBID}/${phen_file}/;
sed "s/NA//g" ${solar_dir}/perms/${phen_file}.csv > /lscratch/${SLURM_JOBID}/${phen_file}/;
for v in `seq $v1 $v2`; do
    vox=`printf "%06d" $v`;
    mkdir /lscratch/${SLURM_JOBID}/${phen_file}/${vox};
    cd /lscratch/${SLURM_JOBID}/${phen_file}/${vox}/;
    cp ../pedigree.csv ../procs.tcl ../${phen_file}.csv ./;
    solar run_phen_var $phen_file v${vox};
    mv i_v${vox}/polygenic.out ../v${vox}_polygenic.out;
done;
cp ../v*_polygenic.out ${tmp_dir}/${phen_file}/;
cd /lscratch/${SLURM_JOBID};
rm -rf /lscratch/${SLURM_JOBID}/${phen_file};
