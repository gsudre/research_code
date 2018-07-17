# Copies anatomical and resting raw DICOMs to cluster to be further converted to HEAD and BRIK
m=$1
out_dir=$2
net_dir=$3


ssh -qt bw "if [ ! -d ${out_dir}/mprages_dcm ]; then mkdir ${out_dir}/mprages_dcm/; fi";
ssh -qt bw "if [ ! -d ${out_dir}/rest_dcm ]; then mkdir ${out_dir}/rest_dcm/; fi";

cd $net_dir/best_mprages
echo Copying $m MPRAGE
gtar cf - ${m} | ssh -q bw "tar xf - -C ${out_dir}/mprages_dcm/";

# find name of date folders
ls -1 $net_dir/data_by_maskID/${m}/ | grep -e ^20 > ~/tmp/date_dirs;

# for each date folder, check for resting scans
ssh -qt bw "if [ ! -d ${out_dir}/rest_dcm/${m} ]; then mkdir ${out_dir}/rest_dcm/${m}; fi";
echo Copying $m rsFMRI
cnt=1
while read d; do
    grep rest $net_dir/data_by_maskID/${m}/${d}/*README* > ~/tmp/rest;
    awk '{for(i=1;i<=NF;i++) {if ($i ~ /Series/) print $i}}' ~/tmp/rest | sed "s/Series://g" > ~/tmp/rest_clean
    cd $net_dir/data_by_maskID/${m}/${d}/
    # for each rest line
    while read line; do
        mr_dir=`echo $line | sed "s/,//g"`;
        gtar cf - ${mr_dir} | ssh -q bw "tar xf - -C ${out_dir}/rest_dcm/${m}/";
        let cnt=$cnt+1;
    done < ~/tmp/rest_clean;
done < ~/tmp/date_dirs;
