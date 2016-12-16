net_dir=/Volumes/Labs/Shaw
while read m; do
	ls -1 $net_dir/data_by_maskID/${m}/ | grep -e ^20 > /tmp/date_dirs4;
	cnt=1;
	while read d; do
		grep rest $net_dir/data_by_maskID/${m}/${d}/*README* > /tmp/rest4;
		# for each rest line
		while read line; do
			let cnt=$cnt+1;
		done < /tmp/rest4;
	done < /tmp/date_dirs4;
	# spit out how many files we converted
	let cnt=$cnt-1;
	echo "${m} ${cnt}" >> ~/tmp/counts2.txt
done < ~/tmp/batch2
