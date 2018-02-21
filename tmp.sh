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

# copying resting files for ayaka
net_dir=/Volumes/Shaw
while read m; do
	if [ ! -d ${net_dir}/Irritability_project/DICOM_resting/${m} ]; then
		echo $m;
		ls -1 $net_dir/data_by_maskID/${m}/ | grep -e ^20 > /tmp/date_dirs;
		while read d; do
			cd $net_dir/data_by_maskID/${m}/${d};
			grep rest *README* | cut -d "," -f 3 | cut -d ":" -f 2 > /tmp/rest;
			mkdir ${net_dir}/Irritability_project/DICOM_resting/${m};
			# for each rest line
			while read line; do
				cp -r $line ${net_dir}/Irritability_project/DICOM_resting/${m};
			done < /tmp/rest;
		done < /tmp/date_dirs;
	fi;
done < ${net_dir}/Irritability_project/DICOM_resting/ids.txt


# checking how many good TRs we have, and how many were removed
while read subj; do
	 s=`echo $subj | sed -e 's/R//'`
     echo $s;
	 if [ -d /Volumes/Shaw/data_by_maskID/${s}/afni/${s}.rest.subjectSpace.results/ ]; then
	 	mydir=/Volumes/Shaw/data_by_maskID/${s}/afni/${s}.rest.subjectSpace.results/
	 elif [ -d /Volumes/Shaw/data_by_maskID/${s}/afni/${s}.rest.example11_HaskinsPeds.results/ ]; then
	 	mydir=/Volumes/Shaw/data_by_maskID/${s}/afni/${s}.rest.example11_HaskinsPeds.results/
	 else
	 	mydir=/Volumes/Shaw/data_by_maskID/${s}/afni/${s}.rest.example11.results/
	 fi
     good_trs=`1d_tool.py -infile ${mydir}/X.Xmat.1D -show_trs_uncensored comma`;
     array=($(echo ${good_trs} | tr "," "\n"));
	 censored=`1d_tool.py -infile ${mydir}/X.Xmat.1D -show_trs_censored space`;
     echo ${s},${censored},${#array[@]} >> /Volumes/Shaw/tmp/for_ayaka/afni_trs.csv;
done < /Volumes/T/Resting_adult/ids.txt