#!/bin/sh
# Copies over only the files necessary for DIFFCALC, after DIFFPREP DMC.

maskids=$1
start_dir=`pwd`
tmp_script=ssh_pipes.sh

# for each mask id in the file
while read m; do 
    echo "Working on ${m}"    

    # piping inside the loop was breaking it. Will need to do it later. -n flag didn't work because I actually need the stdin pipe.
    echo "echo \"Copying over eDTI files for ${m}\"" >> $tmp_script
    echo "ssh -q biowulf.nih.gov \"mkdir /scratch/ncr/${m}\"" >> $tmp_script
    echo "ssh -q biowulf.nih.gov \"mkdir /scratch/ncr/${m}/edti_proc\"" >> $tmp_script
    echo "cd /mnt/shaw/data_by_maskID/${m}/edti_proc" >> $tmp_script 
    echo "tar czf - edti_DMC* | ssh -q biowulf2.nih.gov \"cd /scratch/ncr/${m}/edti_proc/; tar xzf -\"" >> $tmp_script

done < $maskids

echo "cd ${start_dir}" >> $tmp_script
bash ${tmp_script}
rm $tmp_script

