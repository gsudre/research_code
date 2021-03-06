# Convert raw DICOMs to HEAD and BRIK, structural and functional
maskids=$1
out_file=$2
net_dir=$3
while read m; do
	echo $m
	# only continue if we don't have an afni folder already, or if there is a
	# good mprage selected for the maskid
	# if [ -d $net_dir/data_by_maskID/${m}/afni ] || [ ! -d $net_dir/best_mprages/${m}/ ]; then
	# 	echo "Skipping...";
	# else
		mkdir $net_dir/data_by_maskID/${m}/afni
		# find name of date folders
		ls -1 $net_dir/data_by_maskID/${m}/ | grep -e ^20 > ~/tmp/date_dirs;
		cd $net_dir/data_by_maskID/${m}/afni
		rm mprage*
		# converting structural
		Dimon -infile_prefix "$net_dir/best_mprages/${m}/*.dcm" \
			-gert_to3d_prefix mprage -gert_create_dataset

		# for each date folder, check for resting scans
		rm rest*BRIK rest*HEAD
		cnt=1
		while read d; do
			grep rest $net_dir/data_by_maskID/${m}/${d}/*README* > ~/tmp/rest;
			awk '{for(i=1;i<=NF;i++) {if ($i ~ /Series/) print $i}}' ~/tmp/rest | sed "s/Series://g" > ~/tmp/rest_clean
			# for each rest line
			while read line; do
				mr_dir=`echo $line | sed "s/,//g"`;
				Dimon -infile_prefix "../${d}/${mr_dir}/*.dcm" \
					-gert_to3d_prefix rest${cnt} -gert_create_dataset
				let cnt=$cnt+1;
			done < ~/tmp/rest_clean;
		done < ~/tmp/date_dirs;

		# spit out how many files we converted
		let cnt=$cnt-1;
		echo "${m},${cnt}" >> $out_file
	# fi;
done < $maskids
