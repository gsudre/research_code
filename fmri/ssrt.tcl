#!/usr/local/bin/tclsh
#04-09-08 1016 finding too many correct for go trials comp to volume scripts
#04-12-06 0948 stop inhibit 's' variable names see sumsi and gort.tcl
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
if {$argc==0} { 
  puts "Usage:  tc ssrt eventfile.rt"
  puts "\nwhere eventfile is chi,chg,sti,stg"
  return 0
}
set sbj [lindex $argv 0]

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
append outfnm ".ssr"
append fnmsrt "srt.ssr"
#override above use file in command line as input
if {$argc>0} { set fnm [lindex $argv 0]}
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
#   set totnum [lindex $line 2]
    set totnum [lindex $line 1]
    set totnum [string trim $totnum \,]
    continue
  }
  lappend lstbuf $line
}
#puts "Sort this|$lstbuf|"
set srtbuf1 [lsort -integer -index 0 $lstbuf]
puts "totnum from file=$totnum"
#gets stdin getch
#puts "Sorted|$srtbuf1|"
#gets stdin getch
#set srtbuf1 [lsort -integer -index 2 $buffer]
#set srtbuf2 [lsort -integer -index 2 [array names $buffer]]
##################
set out [open $outfnm w]
puts $out "Read from '$fnm'"
puts $out "TotRT   Trial  RESP  InhDly"
#set nn -1
set nn 0
foreach ll $srtbuf1 {
  puts $out $ll
  incr nn
  set gort($nn) [lindex $ll 0]
}
puts "nn=$nn out of totnum=$totnum"
#gets stdin getch

#puts "Percent SSRT (interp)"
puts $out "Percent SSRT (interp) $nn of $totnum"
foreach pct "50 63 70 75 80 85 87 90 95" {
  foreach line [split $srtbuf1 \n] {
#   set indx [expr $pct*$totnum/100]
#   set fidx [format "%5.3f" [expr $pct*$totnum/100.]]
    set indx [expr $pct*$nn/100]
    #check if this is valid CAUTION################
    if {$indx==0} {set indx 1}
    set fidx [format "%5.3f" [expr $pct*$nn/100.]]
#   puts "Int idx=$indx Flt idx=$fidx"
#   gets stdin getch
    if {$indx==$fidx} {
      set ssrt $gort([expr int($indx)])
#     puts "$pct ssrt=$ssrt  Index $indx"
      puts $out "$pct ssrt=$ssrt  Index $indx"
    } else {
      set xxx [expr int($indx)]
      set xp1 [expr $xxx+1]
      if {$xp1>=$nn} {
        set ssrt $gort($xxx)
#       puts "$pct ssrt=$ssrt  Index $indx"
        puts $out "$pct ssrt=$ssrt  Index $indx"
      } else {
#       puts "Average for indices $xxx and $xp1 = $gort($xxx) and $gort($xp1)"
        set ssrt [expr ($gort($xxx)+$gort([expr $xxx+1]))/2]
#       puts "$pct ssrt=$ssrt  Interpolate between $xxx and $xp1"
        puts $out "$pct ssrt=$ssrt  Interpolate between $xxx and $xp1"
      }
    }
#   gets stdin getch
  }
}
