# Copies anatomical and resting raw DICOMs to cluster to be further converted to
# HEAD and BRIK. This version of the script uses the Globus service, which can
# be much faster than using tar.
# Usage: bash copy_rest_files_globus.sh maskids.txt /data/NCR_SBRB/tmp/ /Volumes/Shaw/

maskid_file=$1
out_dir=$2
net_dir=$3

hpc=e2620047-6d04-11e5-ba46-22000b92c6ec
caterpie=74b32b98-a3aa-11e7-adbf-22000a92523b
myfile=~/tmp/transfers_suma.dat

ssh -qt helix.nih.gov "if [ ! -d ${out_dir}/dcm_mprage ]; then mkdir ${out_dir}/dcm_mprage/; fi";
ssh -qt helix.nih.gov "if [ ! -d ${out_dir}/dcm_rsfmri ]; then mkdir ${out_dir}/dcm_rsfmri/; fi";

rm -rf $myfile
for m in `cat $maskid_file`; do 
    echo "--recursive ${net_dir}/best_mprages/${m}/ ${out_dir}/dcm_mprage/${m}/" >> $myfile;

    # find name of date folders
    ls -1 $net_dir/MR_data_by_maskid/${m}/ | grep -e ^20 > ~/tmp/date_dirs;

    # for each date folder, check for resting scans
    cnt=1
    while read d; do
        grep rest $net_dir/MR_data_by_maskid/${m}/${d}/*README* > ~/tmp/rest;
        awk '{for(i=1;i<=NF;i++) {if ($i ~ /Series/) print $i}}' ~/tmp/rest | sed "s/Series://g" > ~/tmp/rest_clean
        while read line; do
            mr_dir=`echo $line | sed "s/,//g"`;
            echo "--recursive ${net_dir}/MR_data_by_maskid/${m}/${mr_dir}/ ${out_dir}/dcm_rsfmri/${m}/${mr_dir}/" >> $myfile;
            let cnt=$cnt+1;
        done < ~/tmp/rest_clean;
    done < ~/tmp/date_dirs;
done;
