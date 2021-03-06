phen_file=$1
v1=$2
v2=$3
tmp_dir=~/data/tmp/

solar_dir=/data/sudregp/heritability_change/

mkdir ${tmp_dir}/${phen_file}
mkdir /lscratch/${SLURM_JOBID}/${phen_file}
# making sure we only access the network once
cp ${solar_dir}/pedigree.csv ${solar_dir}/procs.tcl /lscratch/${SLURM_JOBID}/${phen_file}/;
sed "s/NA//g" ${solar_dir}/perms/${phen_file}.csv > /lscratch/${SLURM_JOBID}/${phen_file}/${phen_file}.csv;
for v in `seq $v1 $v2`; do
     vox=`printf "%06d" $v`;
     mkdir /lscratch/${SLURM_JOBID}/${phen_file}/${vox};
     cd /lscratch/${SLURM_JOBID}/${phen_file}/${vox}/;

     ln ../pedigree.csv ../procs.tcl ../${phen_file}.csv .

     solar run_phen_var $phen_file v${vox};
     mv i_v${vox}/polygenic.out ../v${vox}_polygenic.out;
     # prevents local directory from growing unnecessarily
     cd ..;
     rm -rf ${vox};
done;

tar -czf ${phen_file}_${v1}to${v2}.tgz v*_polygenic.out
cp ${phen_file}_${v1}to${v2}.tgz ${tmp_dir}/${phen_file}/

cd /lscratch/${SLURM_JOBID};
rm -rf /lscratch/${SLURM_JOBID}/${phen_file};
