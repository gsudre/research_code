# Copies surrogate cdiflist files for subjects that didn't have it in the E folder for unspacified reasons
maskids=~/tmp/all_dti_08042016.txt
while read m; do
	echo $m
	# find name of E folders
	ls -1 /mnt/shaw/data_by_maskID/${m}/ | grep -e ^E > /tmp/Edirs
	# might need to create a E folder
	ndirs=`cat /tmp/Edirs | wc -l`
	if [ $ndirs == 0 ]; then
		echo "Creating E0000 folder"
		mkdir /mnt/shaw/data_by_maskID/${m}/E0000;
		echo "E0000" > /tmp/Edirs
	fi;
	if grep -q cdiflist08 /mnt/shaw/data_by_maskID/${m}/2*/*README*; then
		cdi=8
	else
		cdi=9
	fi;
	# for each E folder, check on cdiflist
	while read d; do
		norig_cdi=`ls -1 /mnt/shaw/data_by_maskID/${m}/E*/cdiflist0* | wc -l`;
		if [ ! -e /mnt/shaw/data_by_maskID/${m}/${d}/cdiflist0${cdi} ]; then
			echo "Copying cdiflist for ${m}";
			cp /mnt/shaw/tmp/cdiflist0${cdi} /mnt/shaw/data_by_maskID/${m}/${d}/cdiflist0${cdi}_surrogate;
		fi;
	done < /tmp/Edirs;
done < $maskids