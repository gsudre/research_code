# uses GNU parallel to run a range of voxels in the same node, but writes
# directly to network so we don't lose our results. 
data_file=$1
sx=$2
v1=$3
v2=$4
tmp_dir=$5
rnd_seed=$6

cd /lscratch/${SLURM_JOBID};
cp $data_file ./;
for v in `seq $v1 $v2`; do
    echo Y${v} > Y${v}.txt;
    echo Y${v} >> var_list.txt;
done

if [ ! -d $tmp_dir ]; then
    mkdir $tmp_dir;
fi;

cat var_list.txt | parallel -j $SLURM_CPUS_PER_TASK --max-args=1 \
    Rscript ~/research_code/ctsem_voxel_developmental_time_3_timepoints.R \
        `basename $data_file` \
        $sx {} ${tmp_dir}/${fbase}_${sx}_{}.csv $rnd_seed;
