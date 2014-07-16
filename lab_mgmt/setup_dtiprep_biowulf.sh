#!/bin/sh

maskids=$1
batchFile=~/tortoise_in_biowulf/tortoise.bat
start_dir=`pwd`

cp ~/tortoise_in_biowulf/tortoise_template.bat ${batchFile}
suffix=''
# for each mask id in the file
while read m; do 
    echo "Copying over eDTI files for ${m}"
    # # copying over the necessary files
    ssh -nq biowulf.nih.gov "mkdir ~/data/tortoise/${m}"
    cd /mnt/neuro/data_by_maskID/${m}
    # piping is not really working, so I'll just tar and copy it over. It'll will still be faster, I hope
    tar czf tmp.tar.gz edti edti_proc
    scp -q tmp.tar.gz biowulf.nih.gov:~/data/tortoise/${m}/
    ssh -nq biowulf.nih.gov "cd ~/data/tortoise/${m}; tar xzf tmp.tar.gz; rm tmp.tar.gz"
    rm tmp.tar.gz

    # setting up XML file
    cp ~/tortoise_in_biowulf/0000_template.xml ~/tortoise_in_biowulf/${m}.xml
    perl -p -i -e "s/0000/${m}/g" ~/tortoise_in_biowulf/${m}.xml
    scp -q ~/tortoise_in_biowulf/${m}.xml bw:~/tortoiseXMLfiles/
    rm ~/tortoise_in_biowulf/${m}.xml

    # adding mask id to the current batch file
    echo "./diffprep.sh \"'/home/sudregp/tortoiseXMLfiles/${m}.xml'\" &" >> ${batchFile}

    # setup batch file suffix
    suffix=${suffix}'_'${m}
done < $maskids

echo "wait" >> ${batchFile}
mv ${batchFile} ~/tortoise_in_biowulf/tortoise${suffix}.bat
scp -q ~/tortoise_in_biowulf/tortoise${suffix}.bat bw:~/scripts/
echo "Batch name: tortoise${suffix}.bat"
cd $start_dir