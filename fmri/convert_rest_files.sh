# Convert raw DICOMs to HEAD and BRIK, structural and functional
maskids=$1
out_file=$2
while read m; do
	echo $m
	# only continue if we don't have an afni folder already, or if there is a good mprage selected
	# for the maskid
	# if [ -d /mnt/shaw/data_by_maskID/${m}/afni ] || [ ! -d /mnt/shaw/best_mprages/${m}/ ]; then
	# 	echo "Skipping...";
	# else
		mkdir /mnt/shaw/data_by_maskID/${m}/afni
		# find name of date folders
		ls -1 /mnt/shaw/data_by_maskID/${m}/ | grep -e ^20 > /tmp/date_dirs
		cd /mnt/shaw/data_by_maskID/${m}/afni
		# converting structural
		# Dimon -infile_prefix "/mnt/shaw/best_mprages/${m}/*.dcm" -gert_to3d_prefix mprage -gert_create_dataset

		# for each date folder, check for resting scans
		cnt=1
		while read d; do
			grep rest /mnt/shaw/data_by_maskID/${m}/${d}/*README* > /tmp/rest;
			# for each rest line
			while read line; do
				stringarray=($(echo $line | tr "," "\n"));
				mr=($(echo ${stringarray[2]} | tr ":" "\n"));
				mr_dir=${mr[1]};
				Dimon -infile_prefix "../${d}/${mr_dir}/*.dcm" -gert_to3d_prefix rest${cnt} -gert_create_dataset
				let cnt=$cnt+1;
			done < /tmp/rest;
		done < /tmp/date_dirs;

		# spit out how many files we converted
		let cnt=$cnt-1;
		echo "${m},${cnt}" >> $out_file
	# fi;
done < $maskids