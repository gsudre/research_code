#!/bin/sh

maskids=$1

# adding ssh-key to shell (needed for sbrbmeg)
exec /usr/bin/ssh-agent $SHELL
ssh-add ~/.ssh/id_rsa_helix

# for each mask id in the file
while read m; do 
    echo 'Working on maskid' $m

    # saving original edti_proc folder
    cp -rv /mnt/neuro/data_by_maskID/${m}/edti_proc /mnt/neuro/data_by_maskID/${m}/edti_proc_beforeDIFFPREP

    # copying over the generated files
    scp -r bw:~/data/tortoise/${m}/edti_proc /mnt/neuro/data_by_maskID/${m}/
done < $maskids