# uses GNU parallel to run a range of voxels in the same node
phen_file=$1
var_list=$2
tmp_dir=/data/sudregp/tmp/

solar_dir=/data/sudregp/heritability_change/

mkdir ${tmp_dir}/${phen_file}
mkdir /lscratch/${SLURM_JOBID}/${phen_file}
# making sure we only access the network once
cp ${solar_dir}/pedigree.csv ${solar_dir}/procs.tcl /lscratch/${SLURM_JOBID}/${phen_file}/;
sed "s/NA//g" ${solar_dir}/${phen_file}.csv > /lscratch/${SLURM_JOBID}/${phen_file}/${phen_file}.csv;

voxel_work() { 
     vox=`printf "%06d" $1`;
     phen_file=$2;
     mkdir /lscratch/${SLURM_JOBID}/${phen_file}/${vox};
     cd /lscratch/${SLURM_JOBID}/${phen_file}/${vox}/;

     ln ../pedigree.csv ../procs.tcl ../${phen_file}.csv .

     solar run_phen_var $phen_file v${vox};
     mv i_v${vox}/polygenic.out ../v${vox}_polygenic.out;
     # prevents local directory from growing unnecessarily
     cd ..;
     rm -rf ${vox};
}
export -f voxel_work

cat $var_list | parallel -j $SLURM_CPUS_PER_TASK --max-args=1 voxel_work {} $phen_file;

cd /lscratch/${SLURM_JOBID}/${phen_file}
fname=`basename $var_list`;
tar -czf ${phen_file}_${fname}.tgz v*_polygenic.out
cp ${phen_file}_${fname}.tgz ${tmp_dir}/${phen_file}/

cd /lscratch/${SLURM_JOBID};
rm -rf /lscratch/${SLURM_JOBID}/${phen_file};
