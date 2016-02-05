#!/bin/sh

maskids=$1
start_dir=`pwd`
tmp_script=ssh_pipes.sh

# for each mask id in the file
while read m; do 
    echo "Working on ${m}"    

    # piping inside the loop was breaking it. Will need to do it later. -n flag didn't work because I actually need the stdin pipe.
    echo "echo \"Copying over eDTI files for ${m}\"" >> $tmp_script
    echo "ssh -q biowulf.nih.gov \"mkdir ~/data/tortoise/${m}\"" >> $tmp_script
    echo "ssh -q biowulf.nih.gov \"mkdir ~/data/tortoise/${m}/edti_proc\"" >> $tmp_script
    echo "cd /mnt/neuro/data_by_maskID/${m}/edti_proc" >> $tmp_script 
    echo "tar czf - edti.* edti_DMC* | ssh -q biowulf.nih.gov \"cd ~/data/tortoise/${m}/edti_proc/; tar xzf -\"" >> $tmp_script

done < $maskids

echo "cd ${start_dir}" >> $tmp_script
bash ${tmp_script}
rm $tmp_script

