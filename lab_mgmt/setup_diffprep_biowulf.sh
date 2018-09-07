#!/bin/sh

maskids=$1
batchFile=~/tortoise_in_biowulf/tortoise.bat
start_dir=`pwd`
bw_dir=/data/NCR_SBRB/tmp/tortoise/
data_dir=/mnt/shaw/data_by_maskID/
tmp_script=ssh_pipes.sh

# for each mask id in the file
while read m; do 
    echo "Working on ${m}"    

    cp ~/tortoise_in_biowulf/tortoise_template.bat ${batchFile}
    suffix=''

    # piping inside the loop was breaking it. Will need to do it later. -n flag didn't work because I actually need the stdin pipe.
    echo "echo \"Copying over eDTI files for ${m}\"" >> $tmp_script
    echo "ssh -q helix.nih.gov \"mkdir ${bw_dir}/${m}\"" >> $tmp_script
    echo "cd ${data_dir}/${m}" >> $tmp_script
    if [ -d ${data_dir}/${m}/edti_proc ]; then
        echo "gtar czf - edti edti_proc/edti.* | ssh -q helix.nih.gov \"cd ${bw_dir}/${m}; tar xzf -\"" >> $tmp_script
    else
        echo "Could not find edti_proc";
        echo "gtar czf - edti | ssh -q helix.nih.gov \"cd ${bw_dir}/${m}; tar xzf -\"" >> $tmp_script
    fi

    # setting up XML file
    cp ~/tortoise_in_biowulf/0000_template.xml ~/tortoise_in_biowulf/${m}.xml
    perl -p -i -e "s/0000/${m}/g" ~/tortoise_in_biowulf/${m}.xml
    if [ -e ${data_dir}/${m}/edti/t2_struc_midsag_acpc.nii ]; then
        struct_fname=t2_struc_midsag_acpc.nii;
    elif [ -e ${data_dir}/${m}/edti/t2_struc_acpc.nii ]; then
        struct_fname=t2_struc_acpc.nii;
    else
        struct_fname=t2_struc.nii;
    fi
    perl -p -i -e "s/STRUCT_FILE/${struct_fname}/g" ~/tortoise_in_biowulf/${m}.xml
    scp -q ~/tortoise_in_biowulf/${m}.xml helix.nih.gov:~/tortoiseXMLfiles/
    rm ~/tortoise_in_biowulf/${m}.xml

    # adding mask id to the current batch file
    echo "./diffprep.sh \"'/home/sudregp/tortoiseXMLfiles/${m}.xml'\" &" >> ${batchFile}

    # setup batch file suffix
    suffix=${suffix}'_'${m}

    echo "wait" >> ${batchFile}
    mv ${batchFile} ~/tortoise_in_biowulf/tortoise${suffix}.bat
    scp -q ~/tortoise_in_biowulf/tortoise${suffix}.bat helix.nih.gov:~/scripts/
done < ${maskids}

echo "cd ${start_dir}" >> $tmp_script
bash ${tmp_script}
rm $tmp_script

