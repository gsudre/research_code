#!/usr/local/bin/tclsh
#10-29-03 1023 add extracting information
#10-29-03 0950 inhdly is index 3 for chi.rt index 1 for sti.rt (missing values)
#10-29-03 0930 ssrt is from the gort
#10-29-03 0845 eliminate some debug output for clarity
#05-03-02 1352 ssrtchg.tcl for change trials
#05-03-02 1346 run twice with different file arguments
#05-03-02 1334 getssr1.tcl brute do twice
#05-03-02 1208 was bkwds, chg.rt, % from chi.ave, dly from chi.rt or chi.ssr
#similarly for stop, use stg.rt, % from sti.ave, inhdly (ave) from sti.rt
#05-03-02 1203 rechecking the defn of ssrt:
# gort - inh delay
# go RT from the Go trials for Stop or Stop-Change
# inh delay time btwn go and inhibit for Stop or Stop-Chg
#Run this program for:
# Stp Go: get Nth percent from StG, sub ave Inhibit delay from Stop Inh
# Chg Go: get Nth percent from ChG, sub ave Inhibit delay from Chng Inh
#05-02-02 1054 get average from go file chg.ave
#05-02-02 1037 use percent read from file
#05-02-02 0903 use percent for manual loop
#05-02-02 0638 ssrt for change task but what about stop task?
# no reaction times for correctly inhibited stop trials
#05-01-02 first attempt at adding subject number to file names caused problems
#04-29-02 1041 from ssrt.tcl same code but not run from batch file
#04-26-02 1429 break up into separate runs for analysis?
#04-26-02 1420 read *.ssr files for get ssrt for % program
#04-26-02 1353 enter percent must be separate pgm, getch hangs batch file
#04-25-02 0951 allow input of actual percentage correct and compute ssrt for it
#04-25-02 0947 data analysis of ssrt signal going over subject data & verifying
#02-11-02 1118 analyze using output from new evt.tcl program
#02-08-02 1341 calculates by interpolation
#02-08-02 1240 prob with dos sort
#02-08-02 1216 ssrt2.tcl method 2 using sorted GoRT list
#02-08-02 1202 read again and sub mean GoRT-ss delay
#02-08-02 1159 compute differences note stop-signal delay changes
# mean GoRT
#02-08-02 1133 need sorted for method 2 calc of ssrt
#02-08-02 1127 only one file has valid rt ci, blue
#02-08-02 1115 read cs1ci.rt
#02-08-02 1047 calculate ssrt (version 1?): stop signal reaction time
# SSRT= mean GoRT minus stop-signal delay
# stop-signal delay = interval between go and stop signals = gdur
#02-04-02 1125 computing percentage
#02-04-02 1049 txt2xl.tcl more columnar data

set argc [llength $argv]
if {0} {
if {$argc==0} { 
  puts "Usage:  tc ssrt eventfile"
  puts "\nwhere eventfile is chi,chg,sti,stg"
  return 0
}
}
#set sbj [lindex $argv 0]
#05-03-02 was bkwds, chg.rt, % from chi.ave, dly from chi.rt or chi.ssr
#for change trials
set sbj "chg.rt"
set avg "chi.ave"
set inh "chi.rt"
#for stop trials
#set sbj "stg.rt"
#set avg "sti.ave"
#set inh "sti.rt"
set avf [read [open $avg r]]
set aa [string first "Avg=" $avf]
if {$aa==-1} {
  puts "Error in file '$avg', can't get average RT"
  return 0
}
set ave [string range $avf [expr $aa+4] end]
set aa [string first "msec" $ave]
if {$aa==-1} {
  puts "Error opening file '$avg', can't get average RT"
  return 0
}
set ave [string range $ave 0 [expr $aa-1]]
set ave [string trim $ave \ ]

set pp [string first "%" $avf]
if {$pp==-1} {
  puts "Error in file '$avg', can't get % inhibit"
  return 0
}
# (55.0%) (100.0%)`
set pctinh [string range $avf [expr $pp-8] [expr $pp-1]]
set aa [string first "(" $pctinh]
if {$aa==-1} {
  puts "Error opening file '$avg', can't get % inhibit"
  return 0
}
set pctinh [string range $pctinh [expr $aa+1] end]
set pctinh [string trim $pctinh \ ]

set outfnm $sbj
#set dbgfnm $sbj
set bb [string first "." $outfnm]
if {$bb!=-1} {
  set outfnm [string range $outfnm 0 [expr $bb-1]]
# set dbgfnm $outfnm
  set fnm $outfnm
  set fnmsrt $outfnm
# append outfnm ".ssr"
} else {
  set fnm $sbj.ssr
  set fnmsrt $sbj
}
append outfnm "calc.ssr"
append fnmsrt "srt.ssr"
#override above use file in command line as input
if {$argc>0} { set fnm [lindex $argv 0]}
append fnm ".rt"
puts "$argv0"
puts "Extracting data from file '$fnm'"
if {[file exist $fnm] == 0} {
  puts "File '$fnm' does not exist"
  exit
}
puts "Read from '$fnm'"
#read a line at a time method 2: read buffer and split into lines
#read whole buffer than parse lines after splitting
set buffer [read [open $fnm r]]
#puts "buffer|$buffer|"
set lstbuf {}
foreach line [split $buffer \n] {
  if {[string length $line]==0} {continue}
  if {[string first "Trial" $line]!=-1} {continue}
  if {[string first "Total" $line]!=-1} {
    set avemean [lindex $line 8]
    set totnum [lindex $line 1]
    set totnum [string trim $totnum \,]
    continue
  }
  lappend lstbuf $line
}
puts "Sorting by RT"
set srtbuf1 [lsort -integer -index 0 $lstbuf]
#gets stdin getch
#puts "Sorted|$srtbuf1|"
#gets stdin getch
#set srtbuf1 [lsort -integer -index 2 $buffer]
#set srtbuf2 [lsort -integer -index 2 [array names $buffer]]
##################
set out [open $outfnm w]
puts "Read from '$fnm'"
puts $out "Read from '$fnm'"
puts $out "TotRT   Trial  RESP  InhDly"
set nn 0
set inhdly 0.0
foreach ll $srtbuf1 {
  puts $out $ll
  incr nn
  set gort($nn) [lindex $ll 0]
}
puts "Read all non-zero ([expr $nn+1]) GoRTs"

puts "Get average InhDly from file '$inh'"
#read whole buffer than parse lines after splitting
set buffer [read [open $inh r]]
set dd 0
foreach line [split $buffer \n] {
  if {[string length $line]==0} {continue}
  if {[string first "Trial" $line]!=-1} {continue}
  if {[string first "Total" $line]==-1} {
#   puts "file'$inh'line|$line|"
    incr dd
    set tmp [lindex $line 3]
    if {[string length $tmp]==0} {
      set tmp 0.0
    } else {
      set tmp [expr 1.0*$tmp]
    }
    set inhdly [expr $inhdly+$tmp]
#   puts "InhDly Partial Sum $inhdly for $dd trials"
    continue
  }
}
if {$dd!=0} {
  set inhdly [expr 1.0*$inhdly/$dd]
} else {
  puts "Error in inhibit delay"
  set inhdly 0.0
}
set inhdly [format "%5.1f" $inhdly]
puts "Ave Inh Delay=$inhdly from file '$inh'"
puts "Percent Inhibit=$pctinh"

  #from go file
  set pct $pctinh
  puts $out "For $pct percent"
  puts "Get $pct percent GoRT from '$fnm'"
  
  set indx [expr $pct*$nn/100]
  set fidx [format "%5.3f" [expr $pct*$nn/100.]]
  puts "Int idx=$indx Flt idx=$fidx"
# gets stdin getch
  if {$indx>$nn} { set indx $nn }
  if {$indx==$fidx} {
    set ssrt $gort([expr int($indx)])
    puts "Index $indx"
#   puts "\nPercent $pct ssrt-ave=$ssrt-$ave  Index $indx"
#   puts $out "\nPercent $pct ssrt-ave=$ssrt-$ave  Index $indx"
#   puts "\nPercent $pct ssrt-dly=$ssrt-$inhdly  Index $indx"
#   puts "Index $indx\n\nPercent $pct ssrt-dly=$ssrt-$inhdly"
#   puts $out "Index $indx\n\nPercent $pct ssrt-dly=$ssrt-$inhdly"
  } else {
    set xxx [expr int($indx)]
    set xp1 [expr $xxx+1]
    if {$xp1>$nn} { 
      set ssrt $gort($xxx)
      puts "Index $xxx"
#     puts "\nPercent $pct ssrt-ave=$ssrt-$ave  Index $indx"
#     puts $out "\nPercent $pct ssrt-ave=$ssrt-$ave  Index $indx"
#     puts "Index $indx\n\nPercent $pct ssrt-dly=$ssrt-$inhdly"
#     puts $out "Index $indx\n\nPercent $pct ssrt-dly=$ssrt-$inhdly"
    } else {
      puts "Average for indices $xxx and $xp1=$gort($xxx) and $gort($xp1)"
      puts $out "Average for indices $xxx and $xp1=$gort($xxx) and $gort($xp1)"
#     set ssrt [expr ($gort($xxx)+$gort([expr $xxx+1]))/2]
      set ssrt [expr ($gort($xxx)+$gort([expr $xxx+1]))/2.0]
#     puts "Interp btn $xxx,$xp1\n\nPercent $pct ssrt-dly=$ssrt-$inhdly"
#     puts $out "Interp btn $xxx,$xp1\n\nPercent $pct ssrt-dly=$ssrt-$inhdly"
    }
  }
  puts "\nPercent $pct ssrt-dly=$ssrt-$inhdly=[expr $ssrt-$inhdly] msec"
  puts $out "\nPercent $pct ssrt-dly=$ssrt-$inhdly=[expr $ssrt-$inhdly] msec"
