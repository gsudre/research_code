#!/usr/local/bin/tclsh
#09-19-09 1046 gort11.tcl align with 1.0 remove trials for rt<minrt
#  reads minrt if present, uses value in file, default 100
#05-19-08 1024 gort.tcl fixed calc of chi rt, two cases
#  during inhibit and during second go period
#  note: third parm in chi.sum is placeholder and not used
#05-17-08 0345 gort.tcl moved calc of sum to switch cases not at end
#  fixes calculation of mean rt
#04-10-08 1111 gort.tcl counts match mri volume analysis counts
#  very restricted chi response, not early go1rt==0
#  also checks ihh.acc good response during inhibit
#  if not, check go2.acc good response during go2 blank after inhibit
#04-10-08 1106 gort.tcl extr.stp add inh.acc and go2.acc
#04-10-08 1052 gort(2).tcl all match except chi big difference
#  gort finds 50 correct, volnew finds 3 correct (out of 80)
#04-10-08 0949 gort2.tcl use same method as volnew.tcl  go.acc==1
#04-10-08 0930 gort.tcl do NOT count go correct for responses during blank
#04-09-08 1019 discrepancy for correct counts btwn ssrt behavior and vol scripts
#04-12-06 1149 change for stbsc stbcs no blanks
#04-12-06 1013 for chg task ChI
#04-12-06 1000 for stop task ep1.1 on XP need new 's' variables for StI
#11-21-03 0931 if response 3 during go1, can NOT be correct, no inhibt yet
#11-20-03 1419 different ci si totals than method2 splitc 
#  same total for stop gort and splits
#10-29-03 0805 reduce output for clarity
#10-29-03 0455 document each step, program and purpose
#10-28-03 1300 problems with versions, different parameters
#05-02-02 0752 exiting early in stg.rt at 22nd
#05-02-02 0654 send percentage correct inhibits/goes to ssrt.tcl (or file)
#04-25-02 0946 subj is responding during blank period which is 3000 from start
#04-25-02 0917 check raw data or split off data in chi.spt and sti.spt
#04-25-02 0759 sum may not be correct; too large >3000
#02-26-02 1053 compare go.rt after 22, 44, etc go trials
#02-26-02 0917 need correct go, and correct inhibit?
#02-26-02 0912 does not count blank trials in RT calculations
#02-26-02 0907 might need to reproduce go.rt for each run ie not combined
# req counting trials and stopping when allotted number for each run is reached
# inhibit run: 43 trials = 11 blanks + 11 Go X + 11 Go O + 5 Inh X + 5 Inh O
#02-25-02 1012 updated stpmcs.es with fixes from stpcs.es, copied to stpmsc.es
#02-25-02 0654 check for first response not eventual correct response
#02-11-02 1259 generate batch file to run after running this program from batch
# reads:  subj.rt     writes: subj.ave
#02-11-02 1139 adapting to work with new evt.tcl stop analysis script
#02-08-02 1216 calc ssrt method 2 nn% of sorted GoRT list
#02-08-02 1041 calculating reaction times for go and inh trials
#02-08-02 1013 write to subjcg.rt or subjsg.rt
#02-08-02 1008 output summarized file with computed RTs evrt
#02-08-02 1001 include blank.RT if blank.resp present
#02-08-02 0956 revised stop task completely, different object names
#02-07-02 1649 CAUTION hard coded for Stp fields? no contained in if then
#02-07-02 1646 new version: must check for Go.RT also need Blank.RT
# go part include GoDur if in Blank
#02-07-02 1626 changed proc names: ChG ChB ChI StG StB StI
#02-07-02 1020 revised stop task 
#02-06-02 1109 no response for chg-go or stp-go, don't average no rt to ave
#02-06-02 1002 must look at all 3 possibly 4 RT values, will need anyway for
# computing total reaction time--also will need durations for total rt
#02-06-02 0957 chggo.rt 0 but response is during go2
#02-06-02 0742 include in average only if correct, maintain in/correct counts
#02-06-02 0737 assume that split has already been used to isolate the four
# types: chg-go chg-inh stp-go and stp-inh  ie event the same
#02-04-02 0725 append g if bkgd black, i if bkgd not black ie blue or red
#02-03-02 1551 prepend titles line
#02-01-02 1007 explicit argument list: tc gort stp1h.srt ChgGo Black
#02-01-02 1004 read sorted file, edited to minimum with title line
#01-28-02 1249 eliminated procedure[trial]
#01-27-02 1625 lsearch -exact matches Procedure[Trial]  [] no longer interfere
#01-27-02 1244 select certain sections
#01-27-08 1227 gort.tcl get average of non-zero values in column n
#11-16-01 1206 CAUTION: add to extn list as tasks are added

###############################################################
#09-19-09 discard trials for rt<minrt
#09-04-09 minimum RT value for including in average,unrealistic reaction times
set mnrtfil "minrt"
set minrt 100
if {[file exist $mnrtfil]==0} {
  puts "File '$mnrtfil' does not exist";
  puts "Use default minimum RT of $minrt"
} else {
  #read whole buffer than parse lines
  set buffer [read [open $mnrtfil r]]
  set buffer [string trim $buffer]
  if {[string is digit $buffer]==0} {
    puts "Error: |$buffer| only numbers are allowed in file '$mnrtfil'"
    puts "Use default value for minimum RT of $minrt msec"
  } else {
    set minrt $buffer
    puts "Use value for minimum RT $minrt msec from file '$mnrtfil'"
  }
}
###############################################################

set argc [llength $argv]
if {$argc==0} { 
  puts "Usage:  tc gort file.spt"
  puts "\nwhere file is chi, chg, sti, or stg"
  return 0
}
set sbj [lindex $argv 0]
set outfnm $sbj
set dbgfnm $sbj
set bb [string first "." $outfnm]
if {$bb!=-1} {
  set outfnm [string range $outfnm 0 [expr $bb-1]]
  set dbgfnm $outfnm
  set fnm $outfnm
} else {
  #CAUTION no extension name, default .txt
  set fnm "stp"
  append fnm $sbj.rt
}
#overrides command line parsing above
if {$argc>0} { set fnm [lindex $argv 0]}

if {[file exist $fnm]==0} {puts "File '$fnm' does not exist";exit}
puts "Extracting data from file '$fnm',outfnm=$outfnm"

#read a line at a time: first of two ways p334 Nelson
set ave 0.0
set sum 0.0
set nn 0
set bb 0
set tt 0
#number correct
set cc 0
#number of correct go and correct inhibit trials resp
set csum 0.0
set cg 0
set ci 0
#number of go trials
set gg 0
set evname "Event"
set bgname "BkGd"
set stname "Stimulus"
set evrt 0
#for inhibit delay average
set dly 0.0

#read fields to find from sum.stp
set fields [read [open "sum.stp" r]]
set evfind [lindex $fields 0]
#Chg or Stp
set trials [lindex $fields 1]
set rtname [lindex $fields 2]
set bgfind [lindex $fields 3]

set srtfnm $outfnm
#if {[string first "Chg" $trials]!=-1} { }
if {0} {
  if {[string first "Ch" $trials]!=-1} {
    append outfnm "c"
  } else {
    append outfnm "s"
  }
}
if {[string first "Black" $bgfind]!=-1} {
# append outfnm "g.ave"
  append outfnm ".ave"
  append srtfnm ".rt"
} else {
# append outfnm "i.ave"
  append outfnm ".ave"
  append srtfnm ".rt"
}
append dbgfnm ".dbg"
puts "Writing to file '$outfnm'"
set fid [open $fnm r]
set out [open $outfnm w]
set srt [open $srtfnm w]
set dbg [open $dbgfnm w]

#puts $out "File: $fnm"
puts $out "File: $fnm   File: $rtname    BkGd: $bgfind"
puts $dbg "File: $fnm   File: $rtname    BkGd: $bgfind"
#get first titles line
set line [gets $fid]
#puts $dbg "Titles line\n|$line|"
set idxev [lsearch $line $evname]
set evfind XXX
set idxev 0
set idxrt [lsearch $line $rtname]
set idxbg [lsearch $line $bgname]
set idxst [lsearch $line "Stimulus"]
  #align with mri volnew.tcl
  set idxga [lsearch $line "Go.ACC"]

if {$bgfind=="Black"} {
  puts $srt "GoRT\tTrial\tResp"
  #new version need Go.RT
  set idxgr [lsearch $line "Go.RESP"]
  set idxgt [lsearch $line "Go.RT"]
  set idxbr [lsearch $line "Blank.RESP"]
  set idxbt [lsearch $line "Blank.RT"]
  #new version for go trials
  puts "$evname at $idxev, $rtname at $idxrt, $bgname: $idxbg"
  puts $dbg "$evname at $idxev, $rtname at $idxrt, $bgname: $idxbg"
  puts "idxgr=$idxgr idxbr=$idxbr"
  puts "idxgt=$idxgt idxbt=$idxbt"
  puts "idxgd=1000"
} else {
  puts $srt "TotRT\tTrial\tResp\tInhDly"
# puts "trials|$trials|";gets stdin getch
  if {[string first "ChI" $trials]!=-1} {
    #following applies only to ChI inhibit cases: ChI
    set idxgr [lsearch $line "Go1.RESP"]
    set idxir [lsearch $line "Inh.RESP"]
    set idxg2r [lsearch $line "Go2.RESP"]
    set idxbr [lsearch $line "Blank.RESP"]
    set idxgt [lsearch $line "Go1.RT"]
    set idxit [lsearch $line "Inh.RT"]
    set idxg2t [lsearch $line "Go2.RT"]
    set idxbt [lsearch $line "Blank.RT"]
    #align with mri volume analysis volnew.tcl
    set idxia [lsearch $line "Inh.ACC"]
    set idxg2a [lsearch $line "Go2.ACC"]

  } else {
    #following applies only to StI inhibit
    set idxgr [lsearch $line "Go1s.RESP"]
    set idxir [lsearch $line "Inhs.RESP"]
    set idxg2r [lsearch $line "Go2s.RESP"]
    set idxgt [lsearch $line "Go1s.RT"]
    set idxit [lsearch $line "Inhs.RT"]
    set idxg2t [lsearch $line "Go2s.RT"]
    #special for stbcs stbsc
    set idxbr [lsearch $line "Blank.RESP"]
    set idxbt [lsearch $line "Blank.RT"]
  }

  #only applies to inhibit trials
  set idxgd [lsearch $line "GoDur"]
  set idxid [lsearch $line "InhDur"]
  set idxg2d [lsearch $line "Go2Dur"]

  puts "$evname at $idxev, $rtname at $idxrt, $bgname: $idxbg"
# puts "idxgr=$idxgr idxir=$idxir idxg2r=$idxg2r"
# puts "idxgt=$idxgt idxit=$idxit idxg2t=$idxg2t"
# puts "idxgd=$idxgd idxid=$idxid idxg2d=$idxg2d"
}

while { ! [eof $fid] } { 
  set line [gets $fid]
# puts "Event|$line|"
  if {[string length $line]==0} {continue}
  set nxtline [split $line \t]
  #no longer need since will be split out by event
# if {[string compare $evfind [lindex $nxtline $idxev]]!=0} {continue}
  set evfind [lindex $nxtline $idxev]
  incr tt
  set bkgd [lindex $nxtline $idxbg]
  if {[string compare $bgfind $bkgd]!=0} {continue}
# puts "Hit q to quit";gets stdin getch; if {$getch=="q"} {exit}
  incr nn
  #should check if correct first before including in average?
  #case 1: ChgIn 3 in Chg.RESP or CGo2.RESP
  #case 2: ChgGo X Stimulus and 1 in ChgGo.RESP or Chg.RESP or CGo2.RESP
  #           or O Stimulus and 2 in ChgGo.RESP or Chg.RESP or CGo2.RESP
  #case 3: StpIn 0 in StpGo.RESP and Stp.RESP and SGo2.RESP
  #case 4: StpGo X Stimulus and 1 in StpGo.RESP or Stp.RESP or SGo2.RESP
  #           or Y Stimulus and 2 in StpGo.RESP or Stp.RESP or SGo2.RESP
  set stim [lindex $nxtline $idxst]
  set gr   [lindex $nxtline $idxgr]
  set gt   [lindex $nxtline $idxgt]
  set br   [lindex $nxtline $idxbr]
  set bt   [lindex $nxtline $idxbt]
  #align with volnew go.acc==1 method
  set ga   [lindex $nxtline $idxga]

  if {0} {
    set ir   [lindex $nxtline $idxir]
    set g2r  [lindex $nxtline $idxg2r]
    set it   [lindex $nxtline $idxit]
    set g2t  [lindex $nxtline $idxg2t]
    set gdur [lindex $nxtline $idxgd]
    set idur [lindex $nxtline $idxid]
    set g2dur [lindex $nxtline $idxg2d]
  }


# # puts -nonewline "bkgd|$bkgd|"
# # puts $dbg "bkgd|$bkgd|"
# # puts "bkgd|$bkgd|"
#   # switch $bkgd {
  if {$bkgd == "Black"} {
#     puts -nonewline "stim|$stim|"
      #must discard the baseline blank trials
      if {[string length $stim]==0} {continue}
#     if {$stim==""} {continue}
      incr bb
      #(correct) just go trial counter
      incr cg
      #09-19-09 replace with code that discards trial if rt<minrt
      #align with volnew go.acc==1 method
      if {$ga==1} {
        #09-04-09 only for rt >= 100msec
        set evrt $gt
        if {$evrt>=$minrt} {
          #do not include in average
          incr cc
          set sum [expr $sum+$evrt]
          puts $srt "$evrt\t$cc\tCor"
        }
      } else {
        continue
      }
      if {0} {
        if {$ga=="1"} {
          set evrt $gt
          incr cc
          #partial sum moved here for go trials
          set sum [expr $sum+$evrt]
          puts $srt "$evrt\t$cc\tCor"
        }
      }
    }
    if {$bkgd == "Blue"} {
      set gr   [lindex $nxtline $idxgr]	;#go1.resp
      set ir   [lindex $nxtline $idxir] ;#inh.resp
      set g2r  [lindex $nxtline $idxg2r];#go2.resp
      set it   [lindex $nxtline $idxit] ;#inh.rt
      set g1t  [lindex $nxtline $idxgt] ;#go1.rt
      set g2t  [lindex $nxtline $idxg2t];#go2.rt
      set gdur [lindex $nxtline $idxgd] ;#godur
      set idur [lindex $nxtline $idxid] ;#inhdur
      set g2dur [lindex $nxtline $idxg2d];#go2dur
      #align with mri volnew.tcl analysis
      set ia   [lindex $nxtline $idxia] ;#inh.acc
      set g2a  [lindex $nxtline $idxg2a];#go2.acc
      incr bb
      #check first response not just first 3 response 02-25-02
      if {$g1t>0} {
        set evrt $gt
        #can not be correct, no inhibit yet 11-21-03
        continue
      } 
      #used in volnew.tcl mri analysis
      #if {$g1rt==0 && ($ia==1 || $g2a==1)} { }
      if {$ia==1 || $g2a==1} { 
        if {$ia==1} {
          set evrt [expr $it+$gdur]
        } else {
          set evrt [expr $gdur+$idur+$g2t]
        }
        #partial sum moved here for go trials
        set sum [expr $sum+$evrt]
        incr cc
      } else {
        continue
      }
#     incr cc
      set dly [expr $dly+$gdur]
      puts "gt=$gt it=$it g2t=$g2t gr=$gr ir=$ir g2r=$g2r"
      puts "gdur=$gdur inhdur=$idur eventrt=$evrt"
      #partial sum moved here for change trials
#     set sum [expr $sum+$evrt]
      puts $srt "$evrt\t$cc\t3\t$gdur"
#     gets stdin getch;if {$getch=="q"} {exit}
    }
    if {$bkgd=="Red"} {
      set ir   [lindex $nxtline $idxir]
      set g2r  [lindex $nxtline $idxg2r]
      set it   [lindex $nxtline $idxit]
      set g2t  [lindex $nxtline $idxg2t]
      set gdur [lindex $nxtline $idxgd]
      set idur [lindex $nxtline $idxid]
      incr bb
      if {$gr=="" && $ir=="" && $g2r=="" && $br==""} {
#       puts $dbg "Good Stop Inh: All RTs are 0 gt=$gt it=$it g2t=$g2t bt=$bt"
        incr cc
        set dly [expr $dly+$gdur]
        #inhibit trials,no rt should be 0
        set sum [expr $sum+$evrt]
        puts $srt "\t$cc\t\t$gdur"
      } else {
#       puts $dbg "Bad Stop Inh"
        continue
      }
    }
# #     else {
# # # #   should not get here
# # #     default {
# #     puts $dbg "Baseline trial cg=$cg"
# #     }
#   # }
#   #convert string to number
#   #no, only if 'correct' not here
# # set sum [expr $sum+$evrt]
#   #not used
# # set csum [expr $csum+$evrt]
  puts -nonewline $dbg "Average '$evrt' into sum. "
  puts -nonewline $dbg "Inh Delay $dly "
# puts "Sum for $cc val=$sum"
# puts "Sum for $cc val=$sum\n|$line|"
# puts $dbg "Sum for $cc val=$sum\n|$line|"
  puts $dbg "Sum for $cc val=$sum"
# # puts "Hit q to quit";gets stdin getch; if {$getch=="q"} {exit}
#   }

}

#caution: use cc number correct not nn number of trials detected
puts "$evfind: Total=$tt $bgfind=$bb $cc correct non-zero values Sum=$sum"
puts $out "$evfind: Total=$tt $bgfind=$bb $cc correct non-zero values Sum=$sum"
puts "Number correct cc=$cc"
puts $out "Number correct cc=$cc"
puts $dbg "Number correct cc=$cc"
if {$bb>0 && $cc>0} {
  puts -nonewline \
    "Total $tt, $cc of $bb ([format "%4.1f" [expr 100.*$cc/$bb]]%). "
  puts -nonewline $dbg \
    "Total $tt, $cc of $bb ([format "%4.1f" [expr 100.*$cc/$bb]]%). "
  puts -nonewline $srt \
    "Total $tt, $cc of $bb ([format "%4.1f" [expr 100.*$cc/$bb]]%). "
  puts -nonewline $out \
    "Total $tt, $cc of $bb ([format "%4.1f" [expr 100.*$cc/$bb]]%). "
} else { 
  puts -nonewline  "Total $tt, $cc of $bb. " 
  puts -nonewline $dbg "Total $tt, $cc of $bb. " 
  puts -nonewline $srt "Total $tt, $cc of $bb. " 
  puts -nonewline $out "Total $tt, $cc of $bb. " 
}
if {$cc>0} {
  puts "Avg=[format "%5.0f" [expr $sum/$cc]] msec"
  puts $srt "Avg=[format "%9.4f" [expr $sum/$cc]] msec"
  puts $dbg "Avg=[format "%5.0f" [expr $sum/$cc]] msec"
  puts $out "Avg=[format "%5.0f" [expr $sum/$cc]] msec"
  puts "Inh dly=[format "%5.0f" [expr $dly/$cc]] msec"
  puts $dbg "Inh dly=[format "%5.0f" [expr $dly/$cc]] msec"
  puts $out "Inh dly=[format "%5.0f" [expr $dly/$cc]] msec"
}
puts      "Total $tt. Background $bgfind $bb, $nn found $cc correct"
puts $dbg "Total $tt. Background $bgfind $bb, $nn found $cc correct\n"
#don't write to srt
#puts $srt ""
puts $out "Total $tt. Background $bgfind $bb, $nn found $cc correct"
close $dbg
close $out
close $fid
