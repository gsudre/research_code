# Convert raw DICOMs to HEAD and BRIK, structural and functional
maskids=$1
out_file=$2
while read m; do
	echo $m
	# only continue if we don't have an afni folder already, or if there is a good mprage selected
	# for the maskid
	if [ -d /mnt/shaw/data_by_maskID/${m}/afni ] || [ ! -d /mnt/shaw/best_mprages/${m}/ ]; then
		echo "\tSkipping...";
	else
		mkdir /mnt/shaw/data_by_maskID/${m}/afni
		# find name of date folders
		ls -1 /mnt/shaw/data_by_maskID/${m}/ | grep -e ^20 > /tmp/date_dirs
		cd /mnt/shaw/data_by_maskID/${m}/afni
		# converting structural
		Dimon -infile_prefix "/mnt/shaw/best_mprages/${m}/*.dcm" -gert_to3d_prefix mprage -gert_create_dataset
		# for each date folder, check for resting scans
		cnt=1
		while read d; do
			echo $cnt
			# norig_cdi=`ls -1 /mnt/shaw/data_by_maskID/${m}/E*/cdiflist0* | wc -l`;
			# if [ ! -e /mnt/shaw/data_by_maskID/${m}/${d}/cdiflist0${cdi} ]; then
			# 	echo "Copying cdiflist for ${m}";
			# 	cp /mnt/shaw/tmp/cdiflist0${cdi} /mnt/shaw/data_by_maskID/${m}/${d}/cdiflist0${cdi}_surrogate;
			# fi;
			let cnt=$cnt+1;
		done < /tmp/date_dirs;
done < $maskids