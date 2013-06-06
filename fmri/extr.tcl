#!/usr/local/bin/tclsh
#10-28-03 1440 stop1b
#10-10-03 1141 wof4b afni
#07-12-03 1246 no eof blank line
#07-07-03 1033 extrpa.tcl start over
#05-31-03 1004 debug file for file compare: fc subj.fld extr.tsk
#02-23-03 1634 stw stl stp phase 2 analysis
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
# file created by Excel read from the EPrime *.edat file
#examples of fields to extract
#set keyflds [list "LImage" "RImage" "Mask" "Probe.ACC" "Probe.RT" "Target"]

#CAUTION: add to file extension name list as tasks are added
set extn "stp waf dsn fac dot iap wof wmt smt cnd evl xy fld "

set argc [llength $argv]
if {$argc>0} { set fnm [lindex $argv 0]
} else { 
  puts "Usage:  tc extr \<filename\> \[extr.fld\]"
  puts "\nwhere \<filename\> is the required input file"
  puts "and extr.fld contains the names of the fields to extract"
  return 0
}

set outfnm $fnm
set dbgfnm $fnm
set bb [string first "." $outfnm]
if {$bb!=-1} {set outfnm [string range $outfnm 0 [expr $bb-1]]
} else {
  #CAUTION no extension name, default .txt
  append fnm ".txt"
}
puts "Extracting data from file '$fnm'"

if {[file exist $fnm] == 0} {
  puts "File '$fnm' does not exist"
  exit
}

#check if extraction fields file is 2nd arg, use if so; default extr.fld
if {$argc>1} { set keyfnm [lindex $argv 1]
} else { 
# set keyfnm "extr.fld" 
  #get field names in data lines from extr.fld
  #generic: find extraction file: extr.fld or extr.nnn where nnn=dsn,fac,dot
  set keyfnm "extr."
  #method 1: try reading from list-see list above
# set extn "fld dsn fac dot iap stp wof wmt smt cnd evl"
  foreach ee $extn {
    set tmp "$keyfnm$ee"
#   puts "looking for '$tmp'"
    if {[file exist $tmp]==1} {
      set keyfnm $tmp
      break
    }
  }
}
set bb [string first "." $keyfnm]
if {$bb!=-1} {
  set tmp [string range $keyfnm 0 [expr $bb-1]]
  set tmp [string range $tmp 0 0]
  append outfnm "$tmp.txt"
# append dbgfnm "$tmp.fld"
} else { 
  append outfnm "e.txt" 
# append dbgfnm ".fld" 
}
append dbgfnm ".fld" 
puts "Reading data items to extract from '$keyfnm'"
puts "Writing to file '$outfnm'"
puts "File for comparison '$dbgfnm'"

set fid [open $fnm r]
set out [open $outfnm w]
set dbg [open $dbgfnm w]

#read from file one line per field, must match exactly with EPrime names
set temp [read [open $keyfnm r]]
set temp [split $temp \n]
set keyflds ""
foreach aa $temp { if {[string length $aa]>0} { lappend keyflds $aa } }

#do not get first line full file name in Excel exported file, not SPS file
#filters, if any, are placed after the full pathname and before titles
#checks for end of file otherwise if keyword is not found, program hangs
#caution titlefld must not be used as a filter, must always be in titles line
set titlefld "ExperimentName"
#puts "Searching for titles line containing '$titlefld'"
while { ! [eof $fid] } {
  #get names of parameters
  set titles [gets $fid]
  if {[string first $titlefld $titles]!=-1} { break
  } else { puts $out $titles } 
}
if {[eof $fid]} {
  puts "Did not find titles line containing '$titlefld'"
  puts "Hit any key to continue";gets stdin getch;exit
}
#not titles order but order given in extr.fld
set ii 0
set kk -1
foreach jj $keyflds {
  set ii -1
  foreach hh $titles {
    incr ii
    if {$jj == $hh} {
      incr kk
      set index($kk) $ii
      set fldname($kk) $hh
      break
    }
  }
}
puts "\nFound the following requested fields:\nIndex Field Name"
#puts $dbg "Found the following requested fields:\nIndex Field Name"
for {set jj 0} {$jj<=$kk} {incr jj} {
  puts "[expr $jj+1] $index($jj)    $fldname($jj)"
# puts $dbg "[expr $jj+1] $index($jj)    $fldname($jj)"
  puts $dbg $fldname($jj)
  if {$jj==0} { puts -nonewline $out $fldname($jj)
  } else {
    if {$jj==$kk} { puts $out \t$fldname($jj)
    } else { puts -nonewline $out \t$fldname($jj) }
  }
}
#read a line at a time: first of two ways p334 Nelson
while { ! [eof $fid] } {
    set line [gets $fid]
    if {[string length $line]==0} {continue}
    set ii -1
    set mm 0
    set nxtline [split $line \t]
    #with foreach ll in line, put in extr.fld order not line order
    #have set of indices (file order) to look for
    for {set mm 0} {$mm <=$kk} {incr mm} {
      set ll [lindex $nxtline $index($mm)]
      if {$mm==0} { puts -nonewline $out $ll
      } else { puts -nonewline $out "\t$ll"}
    }
    puts $out ""
}
close $fid
close $out
