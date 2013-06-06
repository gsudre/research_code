#!/usr/local/bin/tclsh
#04-25-02 0947 do need stpgo and chggo for ssrt
#04-25-02 0821 this module does not calculate totrt
#04-25-02 0741 don't need stpgo chggo ssrt
#03-20-02 0807 gort.bat executes but with a long pause: two copies, two tcl exec
#03-20-02 0804 test exec to run batch files
#02-13-02 0727 no longer sorts
#02-11-02 1252 generate batch file for ssrt.tcl program
#02-11-02 1236 need proper sum??.stp file
#02-11-02 1233 create batch file for gort.tcl program
#02-11-02 1047 split up stpcs1.rt file into event blocks
#02-11-02 1034 split by event type column 1 ChG ChI StG StI
#02-11-02 1022 new version, create new file when Event changes
#02-11-02 1018 split evt.tcl output files, leave in exptl order not sorted
#02-06-02 0725 checks for background color in line, now splits up correctly
#02-06-02 0713 added resp field names to sum??.stp now need to ck correctness
#02-06-02 0706 must filter background color and stimulus
#02-06-02 0703 must remove blank trials: 11 per run
# later in gort.tcl gortsi.tcl must exclude/count incorrects vs correct
#02-06-02 0646 two sets for one run? not splitting correctly?
#02-06-02 0622 subj 999 data partial chg trials 
#02-06-02 0610 rem out rmprac line in bat
#02-05-02 1240 not extracting data-without rmprac.tcl config is incorrect
#02-05-02 1026 split.tcl (pilot version splitp.tcl) read subje.txt not fe.txt
#02-04-02 0636 don't write titles line yet until after sort
#02-04-02 0625 write titles line
#02-04-02 0604 prob on /dev/rdsk/c0/t10/d0/s7 Run fsck manually; raid0 activity
#02-04-02 0554 enterprise server rebooted, fsck problems on /dev/rdsk/c0t10d0s0
#02-03-02 1326 split into chg and stop-chg sections
#02-03-03 1240 rmprac.tcl remove practice lines from pilot data:
# skip 1st title line; remove 33 go practice, next 66 (2x 33 stp/chg prac)
# skip next 132 (4x32 plus blankline); remove 66 lines, and save
#11-16-01 1206 CAUTION: add to extn list as tasks are added
#11-16-01 1202 find name of file containing fields to extract extr.fld dsn fac
#09-21-01 0856 display name of output file
#09-20-01 1055 use just first letter of extr field file e or r
#09-20-01 0715 extract from sps formatted file no path line;elim first gets
#09-08-01 1122 extract fields file name if any is appended to file: 3extr.txt
#08-17-01 0443 search for ExperimentName which should always be in titles line
#08-17-01 0407 fixed while 1 check for eof
#07-20-01 1113 if present, take the same order as in the extr.fld file
#06-26-01 1104 read and pass filters line which is btwn path name and titles
#06-22-01 0714 now put in same order as in the file
#06-22-01 0656 read fields from file extr.fld
#06-22-01 0645 count tabs-use set nxtline [split line \t]
#06-22-01 0549 added output of filepath and header to summary file
#06-21-01 2005 extracts header and checks for fields to extract
#06-21-01 1555 extr.tcl extract columns of data from the dotprobe converted 
#read file created for SPSS/Excel read from the EPrime *.edat file
#examples of fields to extract
#set keyflds [list "LImage" "RImage" "Mask" "Probe.ACC" "Probe.RT" "Target"]

#CAUTION: add to file extension name list as tasks are added
set extn "stp evl xy fld "

set argc [llength $argv]
if {$argc==0} { 
  puts "Usage:  tc split \<subjno\>"
  puts "\nwhere \<subjno\> is the subject number for the data file"
  return 0
}

#default arg 1 is subject identifier eg 1 or cs1
set subj [lindex $argv 0]
set fnm $subj.rt 
# append fnm $subj.rt
puts "Extracting data from file '$fnm'"

if {[file exist $fnm] == 0} {
  puts "File '$fnm' does not exist"
  exit
}

set fid [open $fnm r]
set ttl [open "titles" w]
set bat [open "gort.sh" w]
set ssr [open "ssrt.sh" w]

#read a line at a time: first of two ways p334 Nelson
#get titles line
set titl [gets $fid]
puts $ttl $titl
close $ttl

#make sure trial type doesn't match
set lstevt XXX
set evidx 0
while { ! [eof $fid] } {
  set line [gets $fid]
  if {[string length $line]==0} {continue}
  set evt [lindex $line $evidx]
  if {$lstevt=="XXX" || [string compare $lstevt $evt]!=0} { 
    #if new evt type, close last, open new with new name
    if {[string compare $lstevt $evt]!=0 && $lstevt!="XXX"} { close $out }
    set outfnm "$evt.spt"
    puts "Writing to file '$outfnm'"
    if {[string first "CHG" $evt]!=-1} {
      set sumfile "sumcg.stp"
    } elseif {[string first "CHI" $evt]!=-1} {
      set sumfile "sumci.stp"
    } elseif {[string first "STG" $evt]!=-1} {
      set sumfile "sumsg.stp"
    } elseif {[string first "STI" $evt]!=-1} {
      set sumfile "sumsi.stp"
    } else {
      puts "Don't know which sum.stp file configuration to use for '$evt'"
    }
    puts $bat "cp $sumfile sum.stp"
    puts $bat "tclsh gort.tcl $outfnm"
    #do need in order to calc ssrt
#   if {[string first "CHI" $evt]!=-1 || [string first "STI" $evt]!=-1} {
    puts $ssr "tclsh ssrt.tcl $evt.rt"
#   }
    set out [open $outfnm w]
    puts $out $titl
    set lstevt $evt
  }
  puts $out $line
}
close $out
close $fid
close $bat
close $ssr

# puts "Running 'gort.bat' batch file"
# #not allowed with XP
# #exec $env(COMSPEC) /c "gort.bat"

# puts "Running 'ssrt.bat' batch file"
# exec "bash ssrt.bat"

