# uses GNU parallel to run a range of voxels in the same node
data_file=$1
sx=$2
v1=$3
v2=$4
tmp_dir=/data/sudregp/tmp2/

# making sure we only access the network once
cd /lscratch/${SLURM_JOBID};
cp $data_file $var_list ./;

# split the variable files so we have one per processor
rm -rf var_list.txt
for v in `seq $v1 $v2`; do
    echo Y${v} >> var_list.txt;
done
split -da 2 -l $((`wc -l < var_list.txt` /$SLURM_CPUS_PER_TASK)) \
    var_list.txt vlist --additional-suffix=".txt";
fbase=`basename -s .RData.gz $data_file`;

ls -1 vlist*txt > file_list.txt;
cat file_list.txt | parallel -j $SLURM_CPUS_PER_TASK --max-args=1 \
    Rscript ~/research_code/ctsem_voxel_developmental_time_3_timepoints.R \
        `basename $data_file` \
        $sx {} ${fbase}_${sx}_${v1}to${v2}_{}.csv;

tar -czf ${fbase}_${sx}_${v1}to${v2}.tgz *.csv;
cp *.tgz ${tmp_dir}/
