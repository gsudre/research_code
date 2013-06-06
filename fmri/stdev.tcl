#stdev.tcl calculate std dev of rt
#05-17-08 0526 calculates stdev same values as excel formulas
#05-17-08 0440 stdev.tcl calculate stdev
#  SD = sqrt { (sum[(x - averageRT)^2] / (n - 1) }
#10-03-06 1746 dur.tcl each run 6:24 total first time test 27:15
#10-03-06 1649 added start of run and end of run
#10-03-06 1645 added start.finishtime to get elapsed time or use first sel1.ot
#10-03-06 1620 wof win-lose task
#04-26-06 0958 display full tgt duration

set avgparm "Avg="
set hdrparm "RT"
######################MAIN#######################################
#read from tab-delimited, extracted event file
set argc [llength $argv]
if {$argc>0} { 
  set evtfnm [lindex $argv 0]
  set evtfnm [string trimleft $evtfnm "0"]
  set bb [string first "." $evtfnm]
  if {$bb!=-1} {
    set evtfnm [string range $evtfnm 0 [expr $bb-1]]
  }
  set subjno $evtfnm
  set dbgfnm $evtfnm
  set outfnm $evtfnm
  append evtfnm ".rt"
  append outfnm "std.txt"
  append dbgfnm "d.txt"
} else {puts "Usage: $argv0 <subject number>";exit}

#set dbg [open $dbgfnm w]
if {[file exist $evtfnm] == 0} {
  puts "File '$evtfnm' does not exist";
 # puts $dbg "File '$evtfnm' does not exist";
  exit
}
set buffer [read [open $evtfnm r]]
puts "Extracting data from file '$evtfnm'"
#puts $dbg "Extracting data from file '$evtfnm'"

set out [open $outfnm w]
puts "Writing data to file '$outfnm'"

puts $out "Extracting data from file '$evtfnm'"
#puts $out "Writing data to file '$outfnm'"

set runno 0
set endofrun 1
set firstrun 1
#first time through get average at end of file
foreach nxtline [split $buffer \n] {
  if {[string length $nxtline]==0} {continue}
  #parse trailer line
  set aa [string first $avgparm $nxtline]
  if {$aa==-1} {continue}
  set temp [string range $nxtline [expr $aa+4] end]
  set temp [string trim $temp]
# puts "avg line|$temp|"
  set aa [string first " msec" $temp]
  if {$aa==-1} {
    puts "Error in file, no average line"
    continue
  }
  set mean [string range $temp 0 [expr $aa-1]]
  puts "mean=$mean"
  puts $out "mean=$mean"
# gets stdin getch;if {$getch=="q"} {exit}
}
#second time calc diff from ave and (diff from ave)^2
set buffer [read [open $evtfnm r]]
set sumdsq 0.0
#caution need n-1 in formula,start with -1
set num -1
foreach nxtline [split $buffer \n] {
  if {[string length $nxtline]==0} {continue}
  #skip header line
  if {[string first $hdrparm $nxtline]!=-1} { 
#   puts "Header line|$nxtline|\n"
#   puts $dbg "Header line|$nxtline|\n"
    continue
  }
  if {[string first $avgparm $nxtline]!=-1} {break}
  incr num
  set optns [split $nxtline \t]
  #parse data line get rt
  set rt    [lindex $optns  0]
  set diff [expr $rt-$mean]
# puts -nonewline "diff=$diff "
  set diffsq [expr $diff*$diff]
# puts -nonewline "diff squared=$diffsq "
  set sumdsq [expr $sumdsq + $diffsq]
# puts "sumdsq=$sumdsq"
}
puts "sumdsq=$sumdsq  num=[expr $num+1]"
puts $out "sumdsq=$sumdsq  num=[expr $num+1]"
set stdev [expr $sumdsq/$num]
puts "sumdifsq/(n-1)=$stdev"
puts $out "sumdifsq/(n-1)=$stdev"
set stdev [expr sqrt($stdev)]
set stdev [format "%6.3f" $stdev]
puts "stdev=$stdev"
puts $out "stdev=$stdev"
close $out
