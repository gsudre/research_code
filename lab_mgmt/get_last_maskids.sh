ls -1 /Volumes/Labs/Shaw/MR_data/ > ~/tmp/all_people.txt
while read p; do
    ls -1 /Volumes/Labs/Shaw/MR_data/${p}/ > ~/tmp/maskids.txt;
    rm ~/tmp/sorted_maskids.txt;
    touch ~/tmp/sorted_maskids.txt;
    while read n; do
        n=$((10#$n)); # force decimal (base 10)
        echo `printf "%04d\n" $n` >> ~/tmp/sorted_maskids.txt;
    done < ~/tmp/maskids.txt;
    last_maskid=`sort ~/tmp/sorted_maskids.txt | tail -1`;
    bar=(`echo $p | tr '-' ' '`)
    mrn="${bar[1]}"
    nscans=`wc -l ~/tmp/sorted_maskids.txt`
    echo ${mrn},${last_maskid},${nscans} >> ~/tmp/last_ids.txt;
done < ~/tmp/all_people.txt
