#!/bin/bash
# Copy our scans to NNDSP
# GS, 04/2017

ids_file=$1;
while read m; do
    echo $m;
    cd /Volumes/Labs/Shaw/data_by_maskID/${m};
    gtar -zcf ~/tmp/${m}.tar.gz 2*;
    scp ~/tmp/${m}.tar.gz bw:/data/NNDSP/NCR/;
    rm  ~/tmp/${m}.tar.gz;
done < $ids_file
