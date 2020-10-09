# records IP once in a while in a computer with DNS record
myfile=~/tmp/myip.txt;
/bin/date >> $myfile;
/sbin/ifconfig | /usr/bin/grep 165 >> $myfile;
/usr/bin/scp -q $myfile ncrshell01:~/tmp/