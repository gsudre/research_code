#!/bin/sh

maskids=$1
start_dir=`pwd`
bw_dir=/data/NCR_SBRB/tmp/tortoise/
data_dir=/mnt/shaw/data_by_maskID/
bw_templates_dir=~/tortoise_in_biowulf/
tmp_script=ssh_pipes.sh

# prepare batch and xml folders
ssh -q helix.nih.gov "if [ ! -d ${bw_dir}/xml ]; then mkdir ${bw_dir}/xml; fi"
ssh -q helix.nih.gov "if [ ! -d ${bw_dir}/bat ]; then mkdir ${bw_dir}/bat; fi"

# for each mask id in the file
while read m; do 
    echo "Working on ${m}"    

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

    # setting up XML file. Replace 0000 by mask id and struct_File by the 
    # correct filename
    cp ${bw_templates_dir}/0000_template.xml ${bw_templates_dir}/${m}.xml
    perl -p -i -e "s/0000/${m}/g" ${bw_templates_dir}/${m}.xml
    if [ -e ${data_dir}/${m}/edti/t2_struc_midsag_acpc.nii ]; then
        struct_fname=t2_struc_midsag_acpc.nii;
    elif [ -e ${data_dir}/${m}/edti/t2_struc_acpc.nii ]; then
        struct_fname=t2_struc_acpc.nii;
    else
        struct_fname=t2_struc.nii;
    fi
    perl -p -i -e "s/STRUCT_FILE/${struct_fname}/g" ${bw_templates_dir}/${m}.xml
    scp -q ${bw_templates_dir}/${m}.xml helix.nih.gov:${bw_dir}/xml/;
    rm ${bw_templates_dir}/${m}.xml

    # creating batch_file
    batchFile=tortoise_${m}.bat;
    echo "#!/bin/bash" > ${batchFile};
    echo "cd ${bw_dir}/bat;" >> ${batchFile};
    echo "./diffprep.sh \"'${bw_dir}/xml/${m}.xml'\" &" >> ${batchFile}
    echo "wait" >> ${batchFile}
    mv ${batchFile} ${bw_templates_dir}/
    scp -q ${bw_templates_dir}/${batchFile} helix.nih.gov:${bw_dir}/bat/
    
done < ${maskids}

echo "cd ${start_dir}" >> $tmp_script
bash ${tmp_script}
rm $tmp_script

