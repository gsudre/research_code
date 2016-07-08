#!/bin/sh
# This needs to be run in Biowulf! Sends back data to Shaw drive after running DIFFCALC form /scratch

maskids=$1
tmp_script=ssh_pipes.sh
start_dir=`pwd`

# check which subjects ran all the way to the end
while read m; do 
    if [ -d /scratch/ncr/${m}/edti_proc ]; then
        echo 'Working on maskid' $m

        # copying over the generated files
        echo "echo \"Copying results for ${m}\"" >> $tmp_script
        echo "cd /scratch/ncr/${m}" >> $tmp_script
        echo "tar czf - edti_proc | ssh -q sbrbmeg.nhgri.nih.gov \"cd /mnt/shaw/data_by_maskID/${m}; tar xzf -\"" >> $tmp_script
    else
        echo "ERROR: did not find ${m} in directory"
    fi
done < $maskids

echo "cd $start_dir" >> $tmp_script
bash $tmp_script
rm $tmp_script