# Convert raw DICOMs to HEAD and BRIK, structural and functional, after they
# have already been copied to the cluster using copy_rest_files.sh. Better to be
# run in the cluster!
# 
# Usage: bash convert_sorted_rest_files MASKID /data/NCR_SBRB/tmp/dcm_mprage
# /data/NCR_SBRB/tmp/dcm_rsfmri/ /scratch/sudregp/rsfmri/

m=$1
mprage_dir=$2
rsfmri_dir=$3
out_dir=$4

echo Converting $m;

if [ ! -d ${out_dir} ]; then 
    mkdir ${out_dir};
fi

rm -rf $out_dir/${m};
mkdir $out_dir/${m};
cd $out_dir/${m}

Dimon -infile_prefix "$mprage_dir/${m}/*.dcm" -gert_to3d_prefix mprage -gert_create_dataset

cnt=1
for d in `/bin/ls -1 ${rsfmri_dir}/${m}/`; do
    Dimon -infile_prefix "$rsfmri_dir/${m}/${d}/*.dcm" \
        -gert_to3d_prefix rest${cnt} -gert_create_dataset
    let cnt=$cnt+1;
done;
