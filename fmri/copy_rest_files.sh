# Copies anatomical and resting raw DICOMs to cluster to be further converted to
# HEAD and BRIK. 
# Usage: bash copy_rest_files.sh maskid /data/NCR_SBRB/tmp/ /Volumes/Shaw/

m=$1
out_dir=$2
net_dir=$3

ssh -qt helix.nih.gov "if [ ! -d ${out_dir}/dcm_mprage ]; then mkdir ${out_dir}/dcm_mprage/; fi";
ssh -qt helix.nih.gov "if [ ! -d ${out_dir}/dcm_rsfmri ]; then mkdir ${out_dir}/dcm_rsfmri/; fi";

cd $net_dir/best_mprages
echo Copying $m MPRAGE
gtar cf - ${m} | ssh -q helix.nih.gov "tar xf - -C ${out_dir}/dcm_mprage/";

# find name of date folders
ls -1 $net_dir/MR_data_by_maskid/${m}/ | grep -e ^20 > ~/tmp/date_dirs;

# for each date folder, check for resting scans
ssh -qt helix.nih.gov "if [ ! -d ${out_dir}/dcm_rsfmri/${m} ]; then mkdir ${out_dir}/dcm_rsfmri/${m}; fi";
echo Copying $m rsFMRI
cnt=1
while read d; do
    grep rest $net_dir/MR_data_by_maskid/${m}/${d}/*README* > ~/tmp/rest;
    awk '{for(i=1;i<=NF;i++) {if ($i ~ /Series/) print $i}}' ~/tmp/rest | sed "s/Series://g" > ~/tmp/rest_clean
    cd $net_dir/MR_data_by_maskid/${m}/${d}/
    # for each rest line
    echo -e "\tFound" `cat ~/tmp/rest_clean | wc -l` scans.
    while read line; do
        mr_dir=`echo $line | sed "s/,//g"`;
        gtar cf - ${mr_dir} | ssh -q helix.nih.gov "tar xf - -C ${out_dir}/dcm_rsfmri/${m}/";
        let cnt=$cnt+1;
    done < ~/tmp/rest_clean;
done < ~/tmp/date_dirs;
