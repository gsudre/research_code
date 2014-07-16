#!/bin/sh
# This needs to be run in Biowulf!

maskids=$1
tmp_script=ssh_pipes.sh
start_dir=`pwd`

# check which subjects ran all the way to the end
while read m; do 
    if [ -e ~/data/tortoise/${m}/edti_proc/edti_DMC.list ]; then
        echo 'Working on maskid' $m

        # saving original edti_proc folder
        ssh -nq sbrbmeg.nhgri.nih.gov "if [ ! -d /mnt/neuro/data_by_maskID/${m}/edti_proc_beforeDIFFPREP ]; then cp -rv /mnt/neuro/data_by_maskID/${m}/edti_proc /mnt/neuro/data_by_maskID/${m}/edti_proc_beforeDIFFPREP; fi"

        # copying over the generated files
        echo "echo \"Copying results for ${m}\"" >> $tmp_script
        echo "cd ~/data/tortoise/${m}" >> $tmp_script
        echo "tar czf - edti_proc | ssh -q sbrbmeg.nhgri.nih.gov \"cd /mnt/neuro/data_by_maskID/${m}; tar xzf -\"" >> $tmp_script
    else
        echo "ERROR: ${m} did not run properly. No edti_DMC.list"
    fi
done < $maskids

echo "cd $start_dir" >> $tmp_script
bash $tmp_script
rm $tmp_script