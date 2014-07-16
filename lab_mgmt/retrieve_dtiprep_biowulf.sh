#!/bin/sh

maskids=$1
start_dir=`pwd`

# for each mask id in the file
while read m; do 
    echo 'Working on maskid' $m

    # saving original edti_proc folder
    if [ ! -d /mnt/neuro/data_by_maskID/${m}/edti_proc_beforeDIFFPREP ]; then
        cp -rv /mnt/neuro/data_by_maskID/${m}/edti_proc /mnt/neuro/data_by_maskID/${m}/edti_proc_beforeDIFFPREP
    fi

    # copying over the generated files
    cd /mnt/neuro/data_by_maskID/${m}
    ssh -nq biowulf.nih.gov "cd ~/data/tortoise/${m}; tar czf tmp.tar.gz edti_proc"
    scp -q biowulf.nih.gov:~/data/tortoise/${m}/tmp.tar.gz .
    tar -zxf tmp.tar.gz
    rm tmp.tar.gz
    ssh -nq biowulf.nih.gov "rm ~/data/tortoise/${m}/tmp.tar.gz"
    
done < $maskids

# check which subjects ran all the way to the end
while read m; do 
    ls /mnt/neuro/data_by_maskID/${m}/edti_proc/*DMC.list
done < $maskids

cd $start_dir