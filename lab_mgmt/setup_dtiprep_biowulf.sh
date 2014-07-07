#!/bin/sh

maskids=$1
batchFile=~/tortoise_in_biowulf/tortoise.bat

cp ~/tortoise_in_biowulf/tortoise_template.bat ${batchFile}
suffix=''
# for each mask id in the file
while read m; do 
    echo 'Working on maskid' $m

    # copying over the necessary files
    mkdir /tmp/${m}
    scp -r /tmp/${m} bw:~/data/tortoise/
    scp -r /mnt/neuro/data_by_maskID/${m}/edti/ bw:~/data/tortoise/${m}/
    scp -r /mnt/neuro/data_by_maskID/${m}/edti_proc/ bw:~/data/tortoise/${m}/
    scp /mnt/neuro/data_by_maskID/${m}/edti/t2_struc_acpc.nii bw:~/data/tortoise/${m}/
    rmdir /tmp/${m}

    # setting up XML file
    cp ~/tortoise_in_biowulf/0000_template.xml ~/tortoise_in_biowulf/${m}.xml
    perl -p -i -e "s/0000/${m}/g" ~/tortoise_in_biowulf/${m}.xml
    scp ~/tortoise_in_biowulf/${m}.xml bw:~/tortoiseXMLfiles/
    rm ~/tortoise_in_biowulf/${m}.xml

    # adding mask id to the current batch file
    echo "./diffprep.sh \"'/home/sudregp/tortoiseXMLfiles/${m}.xml'\" &" >> ${batchFile}

    # setup batch file suffix
    suffix=${suffix}'_'${m}
done < $maskids

echo "wait" >> ${batchFile}
mv ${batchFile} ~/tortoise_in_biowulf/tortoise${suffix}.bat
scp ~/tortoise_in_biowulf/tortoise${suffix}.bat bw:~/scripts/