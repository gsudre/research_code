#!/bin/sh

maskids=$1
batchFile=~/tortoise_in_biowulf/tortoise.bat
start_dir=`pwd`
tmp_script=ssh_pipes.sh

# for each mask id in the file
while read m; do 
    echo "Working on ${m}"    

    cp ~/tortoise_in_biowulf/tortoise_template.bat ${batchFile}
    suffix=''

    # piping inside the loop was breaking it. Will need to do it later. -n flag didn't work because I actually need the stdin pipe.
    echo "echo \"Copying over eDTI files for ${m}\"" >> $tmp_script
    echo "ssh -q biowulf.nih.gov \"mkdir ~/data/tortoise/${m}\"" >> $tmp_script
    echo "cd /mnt/shaw/data_by_maskID/${m}" >> $tmp_script 
    echo "tar czf - edti edti2 edti_proc edti2_proc | ssh -q biowulf.nih.gov \"cd ~/data/tortoise/${m}; tar xzf -\"" >> $tmp_script

    # setting up XML file
    cp ~/tortoise_in_biowulf/0000_template.xml ~/tortoise_in_biowulf/${m}.xml
    perl -p -i -e "s/0000/${m}/g" ~/tortoise_in_biowulf/${m}.xml
    # creating the one for the other scan
    cp ~/tortoise_in_biowulf/${m}.xml ~/tortoise_in_biowulf/${m}_2.xml
    perl -p -i -e "s/edti/edti2/g" ~/tortoise_in_biowulf/${m}_2.xml
    scp -q ~/tortoise_in_biowulf/${m}*.xml bw:~/tortoiseXMLfiles/
    rm ~/tortoise_in_biowulf/${m}*.xml

    # adding mask id to the current batch file
    echo "./diffprep.sh \"'/home/sudregp/tortoiseXMLfiles/${m}.xml'\" &" >> ${batchFile}
    echo "./diffprep.sh \"'/home/sudregp/tortoiseXMLfiles/${m}_2.xml'\" &" >> ${batchFile}

    # setup batch file suffix
    suffix=${suffix}'_'${m}

    echo "wait" >> ${batchFile}
    mv ${batchFile} ~/tortoise_in_biowulf/tortoise${suffix}.bat
    scp -q ~/tortoise_in_biowulf/tortoise${suffix}.bat bw:~/scripts/
done < ${maskids}

echo "cd ${start_dir}" >> $tmp_script
bash ${tmp_script}
rm $tmp_script

