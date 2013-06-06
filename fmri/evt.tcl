#evntnew.tcl
#10-28-03 1515 output.stp use extr.stp
#02-10-02 1954 fails second part newargs|)| retval 0 and ) encountered
#02-10-02 1939 check if absclk is numeric
#02-10-02 1856 result=1 now prob evaluating absclk and runclk
#02-10-02 1610 need way to select no response sel.RESP = {} or NULL sel.RESP
#02-10-02 1547 note: old fbw fbl fbb now consolidated into fbk
#02-10-02 1541 correctly finding sel=2 20 trials
#02-10-02 1528 >=$nvars var(15) error eliminated
#02-10-02 1513 global set retval 0 in main
#02-10-02 1406 added while in % substitution to get all occurrences
#02-10-02 1348 track down simple or condition, debug off screen
#01-28-02 0644 redo again, forgot zip file from home
#01-27-02 1033 find correct expressions for correct go trials
#01-27-02 0746 found parens not paren changed to prens had one prenS
#01-27-02 0703 skip nulls can't skip whole parser expr
#01-27-02 0653 if nulls are place in parser expr, assume false? ie not satisfied
#01-27-02 0632 prob with missing values inside paren expr
#01-26-02 1741 global result prens
#11-03-01 0934 whole arg taken as one list element!

#note: read from time.nnn reads from TIME block if present in evnt.nnn
#set trialtime "Probe.OnsetTime"
set trialtime "TrialDisplay.OnsetTime"

proc StrStr {pat str} {
  global retval
  set cc [string first $pat $str]
# puts -nonewline "{$pat in $str}"
# if {$cc==-1} {puts "0";return 0} else {puts "1";return 1}
  if {$cc==-1} {return 0} else {return 1}
}
proc Parser {args} {
  global retval prens dbg
  set argc [llength $args]
# puts "\nParser:argc=$argc|args: $args :paren=$prens"
# puts $dbg "\nParser:argc=$argc|args: $args :"
# puts $dbg "Parser: paren=$prens"
# puts "Hit any key, q to quit";gets stdin getch;if {$getch=="q"} {exit}
  if {$argc==0} {return 1}
  set arg1 [lindex $args 0]
  set arg2 [lindex $args 1]
  switch $arg1 {
    ( { 
#     puts -nonewline "( beg grp "
      incr prens
      set newargs [lrange $args 1 end]
      set recur "Parser "
      foreach ll $newargs { append recur " $ll" }
#     puts "Recur call: $recur"
      eval $recur
    }
    ) { 
#     puts -nonewline ") end grp "
      incr prens -1
      set newargs [lrange $args 1 end]
      set recur "Parser "
      foreach ll $newargs { append recur " $ll" }
#     puts "Recur call: $recur"
      eval $recur
    }
    | { 
#     puts -nonewline "| oper "
      set newargs [lrange $args 1 end]
      set recur "Parser "
      foreach ll $newargs { append recur " $ll" }
#     puts "Recur call: $recur"
      eval $recur
    }
    & {
#     puts -nonewline "& oper "
      set newargs [lrange $args 1 end]
      set recur "Parser "
      foreach ll $newargs { append recur " $ll" }
#     puts "Recur call: $recur"
      eval $recur
    }
      
    default { 
#     puts "Args: [lrange $args 0 end]"
      #only if arg2 is arg and not =
      #switch to test for:  = > < >= <= <> !
      #value testop parm
      #depending on test operator, perform appropriate comparison
      #temporarily assume val test parm 
      set begidx 3
      set arg3 [lindex $args 2]
      switch $arg2 {
        \= {
#         puts -nonewline "= test "
          if {$arg1 != $arg3} {
#           puts "Fails = test"
#           puts $dbg "Fails = test begidx=$begidx"
            set retval 0
          } else {set retval 1}
        }
        \> {
          if {$arg1 <= $arg3} {
#           puts "Fails > test"
            set retval 0
          } else {set retval 1}
        }
        \< {
          if {$arg1 >= $arg3} {
#           puts "Fails < test"
            set retval 0
          } else {set retval 1}
        }
        \>\= {
          if {$arg1 <  $arg3} {
#           puts "Fails >= test"
            set retval 0
          } else {set retval 1}
        }
        \<\= {
          if {$arg1 >  $arg3} {
#           puts "Fails <= test"
            set retval 0
          } else {set retval 1}
        }
        \<\> {
          if {$arg1 == $arg3} {
#           puts "Fails <> test"
            set retval 0
          } else {set retval 1}
        }
        default {
          #two successive parms
          set begidx 2
          if {[StrStr $arg1 $arg2]==0} {
#           puts -nonewline "Fails StrStr, continue "
            if {$argc==2} {
#             puts "No more to check, returning 0"
                set retval 0
              return $retval
            } else {
              #check if before &
              if {[string compare [lindex $args 2] \&]==0} {
#               puts "Failed before &, returning 0"
                set retval 0
                return $retval
              }
            }
          } else {set retval 1}
        }
      }
      #check if have more to parse
      #use start index 2 or 3 depending if  pat str or val op parm
      set newargs [lrange $args $begidx end]
#     puts $dbg "newargs|$newargs|"
      if {[llength $newargs]==0} {
#       puts "Done, returning $retval"
        return $retval
      }
      #check if before ) and length 1
      if {[string compare [lindex $args $begidx] \)]==0} {
        if {[string length $newargs]==1} {
          if {$retval==0} { return $retval
          } else {return $retval}
        } else {
#         puts $dbg "Remove ) from expression and continue"
          set newargs [lrange $args [expr $begidx+1] end]
#         puts $dbg "w/o )|$newargs|"
        }
      }
      #check if before &
      if {[string compare [lindex $args $begidx] \&]==0} {
        if {$retval==0} { return $retval}
      }
      #check if before |
      if {[string compare [lindex $args $begidx] \|]==0} {
#       puts $dbg "ck if 1 before |"
        if {$retval==1} { 
          #ck if inside parens
          if {$prens>0} {
            #retval=1 inside ()
#           puts $dbg "look for closing paren"
            set pp [lsearch $args "\)"]
            if {$pp==-1} {
              puts "Error in defn: missing close paren"
              exit
            } else {
              #ignore up to paren, skip
              set newargs [lrange $args [expr $pp+1] end]
#             puts $dbg "after (|$newargs|"
              if {[llength $newargs]==0} {
#               puts $dbg "No more after paren; Done, returning $retval"
                return $retval
              } else {
#               puts $dbg "More after ), continue"
                incr prens -1
              }
            }
          } else {
            # retval=1 before |, not inside (), return 1
            return $retval
          }
        }
      }
      #still have more to parse
      set recur "Parser "
      foreach ll $newargs { append recur " $ll" }
#     puts "Recur call: $recur"
      eval $recur
    }
  }
}
######################MAIN#######################################

#read from tab-delimited, extracted event file
if {$argc>0} { 
  set evtfnm [lindex $argv 0]
  set evtfnm [string trimleft $evtfnm "0"]
  set bb [string first "." $evtfnm]
  if {$bb!=-1} {
    set evtfnm [string range $evtfnm 0 [expr $bb-1]]
  }
# set outfnm "dsn$evtfnm"
  set dbgfnm $evtfnm
  set subjno $evtfnm
  append evtfnm "e.txt"
  append dbgfnm ".dbg"
} else {puts "Usage: $argv0 <subject number>";exit}

puts "Extracting data from file '$evtfnm'"
if {[file exist $evtfnm] == 0} {puts "File '$evtfnm' does not exist";exit}
set buffer [read [open $evtfnm r]]
set dbg [open $dbgfnm w]
#finds which extr.tsk file is present where tsk is the task abbrev
set fldfnm "extr."
#method 2: if present, read file name extension from file: extn.tsk
if {[file exist "extn.tsk"]!=0} {
  set extn [read [open "extn.tsk" r]]
} else {
#method 1: try reading from list
############ CAUTION must be updated with each new experiment ############
set extn "dsn fac dot iap stp wof wmt smt cnd evl xy duk ctf cta ctt fld "
}
############ CAUTION must be updated with each new experiment ############
foreach ee $extn {
  set tmp "$fldfnm$ee"
  if {[file exist $tmp]==1} {
    set fldfnm $tmp
    set extfnm $ee
    break
  }
}
############ CAUTION must be updated with each new experiment ############
#puts "Get fields from '$fldfnm'";gets stdin getch
if {[file exist $fldfnm]==0} {
  puts "No file exists which has names of fields to extract 'extr.fld'"
  puts $dbg "No file exists which has names of fields to extract 'extr.fld'"
  exit
}
#get name of probe/trial onsettime 
if {[file exist time.$extfnm]==0} {
  puts "Can't find 'time.$extfnm' which has slide name used for syncing"
  puts "Should contain: Pic.OnsetTime or TrialDisplay.OnsetTime"
  puts $dbg "Can't find 'time.$extfnm' which has slide name used for syncing"
  puts $dbg "Should contain: Pic.OnsetTime or TrialDisplay.OnsetTime"
  exit
} 
set trialtime [read [open "time.$extfnm" r]]
set trialtime [string trim $trialtime]
puts $dbg "File 'time.$extfnm' trialtime|$trialtime|"

set temp [read [open $fldfnm r]]
set temp [split $temp \n]
set xx -1
set et -1
set vt -1
foreach aa $temp { 
  if {[string length $aa]>0} { 
    incr xx
    set extflds($xx) $aa 
    #isolate special variables: ShowVol.OnsetTime and TrialDisplay.OnsetTime
    if {[string first "ShowVol" $aa]!=-1} {
      puts "ShowVol parameter is index $xx in a data line"
      puts $dbg "ShowVol parameter is index $xx in a data line"
      set vt $xx
    }
    if {[string first $trialtime $aa]!=-1} {
      puts $dbg "trial onsetTime $trialtime parameter is index $xx in data line"
      set et $xx
    }
  } 
}
puts $dbg "Extraction field file '$fldfnm' contains: 0-$xx names"
set fnd [open "evnt.fnd" w]
for {set ii 0} {$ii<=$xx} {incr ii} {
  if {fmod($ii,3)==0} {puts ""}
  puts -nonewline "Idx $ii $extflds($ii)\t"
  puts $dbg "Index $ii $extflds($ii)"
  puts $fnd $extflds($ii)
}
close $fnd
puts $dbg "vt|$vt|et|$et|"

#use above to get file extension
#################new left-to-right 4-fn calculator parser#####
#set cndfnm "cond.$extfnm"
set cndfnm "evnt.$extfnm"
#puts "extfnm|$extfnm|"
if {[file exist $cndfnm] == 0} {
  puts "File '$cndfnm', containing event definitions, does not exist"
  puts "Hit any key to continue";gets stdin getch;exit
}
puts "\nReading event information from input file '$cndfnm'"
set temp [read [open $cndfnm r]]
set temp [split $temp \n]
set evtflds ""
foreach aa $temp { 
  if {[string length $aa]>0} { 
    lappend evtflds $aa 
  } 
}

#read output.nnn to get what parameters to output
#set otpfnm "output.$extfnm"
set otpfnm $fldfnm
if {[file exist $otpfnm] == 0} {
  puts "File '$otpfnm', containing output parameters, does not exist"
  exit
}
puts "Reading output parameter information from input file '$otpfnm'"
set temp2 [read [open $otpfnm r]]
set temp2 [split $temp2 \n]
set yy -1
foreach aa $temp2 { 
  if {[string length $aa]>0} { 
    incr yy
    set ovar($yy) $aa
    set oidx($yy) -1
    for {set ii 0} {$ii<=$xx} {incr ii} {
      if {[string compare $aa $extflds($ii)]==0} {
        set oidx($yy) $ii
        break
      }
    }
  } 
}

#now parse the data and output to rt file
set outfnm "$subjno.rt"
set volfnm "$subjno.vol"
set stsfnm "$subjno.sts"
# append outfnm ".rt"
set out [open $outfnm w]
set vol [open $volfnm w]
set sts [open $stsfnm w]

#EReward LBar RBar TrialDisplay.OnsetTime TrialDisplay.RESP ShowVol.OnsetTime
#TrialDisplay.RT TrialDisplay.ACC Trial
#hchr parser & 90 EReward | 90 LBar 90 RBar
#correct parser 1 TrialDisplay.ACC

puts "Output fields" 
#temporarily remove run header
#puts -nonewline $out "Event\tRun"
puts -nonewline $out "Event"
for {set ii 0} {$ii<=$yy} {incr ii} {
  #header line for excel or spss
  puts -nonewline $out "\t$ovar($ii)"
  puts -nonewline "\t$ovar($ii)"
}
puts $out ""
puts ""

set blockon 0
foreach ee $evtflds { 
# puts $dbg "|$ee|" 
  #extract event identification first item in line
  set evtid [lindex $ee 0]
  set evtid [string toupper $evtid]
  puts "Event $evtid"
  puts $dbg \n$evtid
  set evtcntr 0
  #for new tab-delimited format
# puts -nonewline $vol $evtid
  if {$vt==-1} {puts $vol $evtid 
  } else { puts -nonewline $vol $evtid }
  set defn [lrange $ee 1 end]
  #substitute variable name for every index
# puts "Evt '$evtid', subst var into\n|$defn|"
# puts $dbg "Evt '$evtid', subst var into\n|$defn|"
  puts $sts "Event '$evtid':\n$defn"
  puts $dbg "Event '$evtid':\n$defn"
  puts $vol " Event '$evtid':\n$defn"
  
  #check if specific onsettime parameter is given
  set timdefn ""
  set tim1 [string first "TIME" $defn]
  if {$tim1!=-1} {
#   puts "Last onsettime parameter index et|$et|"
    set tim2 [string last "TIME" $defn]
    if {$tim2!=-1} {
      set timdefn [string range $defn [expr $tim1+5] [expr $tim2-2]]
      set defn [string range $defn [expr $tim2+5] end]
      puts "Time defn|$timdefn|\nEvnt defn|$defn|"
      puts $dbg "Time defn|$timdefn|\nEvnt defn|$defn|"
      set trialtime [string trim $timdefn]
#     puts $dbg "trialtime|$trialtime|"
#     puts "trialtime|$trialtime|"
      #eg Go.OnsetTime
      #eg InstrB InstrC InstrD
      set timoth [lrange $timdefn 2 end]
    } else {
      puts "Error in '$cndfnm', unmatched TIME"
      exit
    }
    #locate new onsettime parameter in event field list
    set temp [read [open $fldfnm r]]
    set temp [split $temp \n]
    set et -1
    for {set zz 0} {$zz<=$xx} {incr zz} {
      set aa [lindex $temp $zz]
#     puts "Check next parm|$aa|"
      if {[string length $aa]>0} { 
        #isolate new onsettime parameter eg TrialDisplay.OnsetTime
        if {[string first $trialtime $aa]!=-1} {
          set et $zz
          puts "$trialtime parm is index $zz in data line"
          break
        }
      } 
    }
    if {$et==-1} {
      puts "CAUTION: OnsetTime parameter '$trialtime' not in data line"
      puts $dbg "CAUTION: OnsetTime parameter '$trialtime' not in data line"
      puts "Will not extract volume data correctly"
      puts $dbg "Will not extract volume data correctly"
#     gets stdin getch
    } 
#   puts "et|$et|"
    puts $dbg "et|$et|"
    puts $vol "Trial OnsetTime parameter $trialtime"
    puts "Trial OnsetTime parameter $trialtime"
  }
  
  #check if block is present
  set blkdefn ""
  set blk1 [string first "BLK" $defn]
  if {$blk1!=-1} {
    set blk2 [string last "BLK" $defn]
    if {$blk2!=-1} {
      set blkdefn [string range $defn [expr $blk1+4] [expr $blk2-2]]
      set defn [string range $defn [expr $blk2+4] end]
      puts "Block defn|$blkdefn|\ndefn|$defn|"
      #eg InstrA Procedure
      set blktest "Parser [lrange $blkdefn 0 1]"
      #eg InstrB InstrC InstrD
      set blkoth [lrange $blkdefn 2 end]
    } else {
      puts "Error in 'cndfnm', unmatched BLK"
      exit
    }
  }
  set blkexp "Parser "
  foreach itm $blkdefn {
    set jj -1
    for {set ii 0} {$ii<=$xx} {incr ii} {
      if {[string compare $extflds($ii) $itm]==0} {
        append blkexp "%$ii "
        set jj $ii
        break
      }
    }
    if {$jj==-1} { append blkexp "$itm " }
  }
  set blkexp [string trim $blkexp \ ]
  if {[string length $blkexp]==6} {
    set blkexp ""
  } else {
    set blkoth [lrange $blkexp 3 end]
    set blkexp [lrange $blkexp 0 2]
  }
  set blkexpsave $blkexp
  if {[string length $blkexp]>0} {
    puts "blkexp|$blkexp|"
    puts $dbg "blkexp|$blkexp|"
    gets stdin getch
  }

  #move to here, should only done once per condition, fill in vars with data
  #use identifiers instead of numeric indices, then get appropriate data
  #eg correct  1 TrialDisplay.ACC
  #replace field name with data from correct position in data line
  set cexp "Parser "
  puts $dbg "Replace field name with data from correct posn in data line"
  #####################################################################
  #prob here if not all fields in extr.tsk are found; counting gets off
  #CAUTION: if in definition, non-variables are used eg numbers
  # then can get a possible match
  foreach num $defn {
    set jj -1
    for {set ii 0} {$ii<=$xx} {incr ii} {
      if {[string compare $extflds($ii) $num]==0} {
        append cexp "%$ii "
        set jj $ii
        puts $dbg "field|$extflds($ii)|at idx ii=$ii"
        break
      }
    }
    if {$jj==-1} { append cexp "$num " }
  }
  #####################################################################
  set cexp [string trim $cexp \ ]
  set cexpsave $cexp
  #good debug
# puts $dbg "Event defn|$cexpsave|"
# puts $sts "Event Definition:\n$cexpsave"
# puts "Event defn|$cexp|";
# puts "Hit any key, q to quit";gets stdin getch;if {$getch=="q"} {exit}

  set runno 0
  set runclk 0
  foreach line [split $buffer \n] {
    if {[string length $line]==0} {continue}
    #parse data line get items
    set optns [split $line \t]
    #check for special ShowVol acquire time first
    #removed hard-code for ShowVol.OnsetTime index 7 dotp, 5 desn
    if {$vt!=-1} {
      set temp [lindex $optns $vt]
      if {[string length $temp]>0} { 
        set runclk $temp 
        #kludge for face task data which has showvol in each line
        if {[string first "ShowVol" $temp]!=-1} {
          incr runno
          puts $vol "\nRun $runno"
        }
        if {[string compare $extfnm "fac"]==-1} { continue }
      }
      #CAUTION: skip rest of parsing for titles line? NO!!!
#     puts $dbg "Skipping parse for this titles line\n|$line|"
#     continue
    } 
    #good but lots of debug
#   puts $dbg "Event line|$line|"
#   puts "Event line|$line|"
    #not true for iaps!!!
    if {$extfnm!="iap"} {
      if {[string length [lindex $optns 0]]==0} {
        continue
      }
    } 
    set varline [split $line \t]
    #get data from current line for event condition checking
    #CAUTION: prob when vars in extr.tsk are not in the evnt line
    set nvars [llength $varline]
#   puts "nvars in data line=$nvars|"
    for {set ii 0} {$ii<$nvars} {incr ii} {
      set var($ii) [lindex $varline $ii]
#     puts "$ii:var|$var($ii)|"
#     puts $dbg "$ii:$var($ii)"
    }
#   puts "Hit any key";gets stdin getch;if {$getch=="q"} {exit}
    #check here (1) if blocking is used, (2) if so if correct blk
    #if in block mode, and but not in block, continue
    #in block mode and in middle of block, check line
    #no block specified, just always check line
    #gets here, in block or just parse line and check if condition is met
    #if block checking is on, ck if find block start or in block or wrong blk
    set blkexp $blkexpsave
    if {[string length $blkexp]>0} {
#     puts -nonewline "Block expr|$blkexp|"
      puts -nonewline $dbg "Block expr|$blkexp|"
      #need to check if already on, then check for other ie next blk markers
      #method: check for all markers?

      #replace var placeholder with data in block expr
      #get data from line subst in test condition
      #new replace %n with data from event line
      for {set ii 0} {$ii<$nvars} {incr ii} {
        set tt [lsearch -exact $blkexp "\%$ii"]
        if {$tt!=-1} {
          puts "At index $tt|repl with|$var($ii)|"
          #now replace %n with tt-th variable
          set blkexp [lreplace $blkexp $tt $tt $var($ii)]
          #have the variable that is being checked 
          set jj $ii
          break
        }
      }
      #have variable that is being tested
      #check if block start test in blkexp; or if block end test in blkoth
      set blkexp [string trim $blkexp \ ]
      puts "new blkexp|$blkexp|"
      puts $dbg "new blkexp|$blkexp|"
#     puts "Hit any key";gets stdin getch;if {$getch=="q"} {exit}
      #check if condition for start of block is met
      set result [eval $blkexp]
      #ck if condition is met eg InstrA Procedure, set blk mode 
      if {$result==1} {
        if {$blockon == 1} {
          #KLUDGE special for IAPS since two instruction slides are in a grp
          if {[string compare $extfnm "iaps"]!=-1} {
            puts "Error: two block markers (groups) in succession?"
            puts $dbg "Error: two block markers (groups) in succession?"
            exit
          }
        } else {
          set blockon 1
          puts "Detected start of block"
          puts $dbg "Detected start of block"
#         puts "Hit any key";gets stdin getch;if {$getch=="q"} {exit}
          continue
        }
      }
      #check here if other markers ie end of block?
      #eg InstrB Procedure
      if {[string first $var($jj) $blkoth]!=-1} {
        puts "Detected start of next block with '$var($jj)'"
        puts $dbg "Detected start of next block with '$var($jj)'"
        set blockon 0
        continue
      }
    } else {
      #blocking not used, parse everything
      set blockon 1
    }
#   puts "Hit any key";gets stdin getch;if {$getch=="q"} {exit}
    
    #not in correct block, don't parse
    if {$blockon==0} {continue}
    set cexp $cexpsave
#   puts $dbg "cexp tmpl|$cexp|"
#   puts "cexp tmpl|$cexp|"
    #new replace %n with data from event line
    for {set ii 0} {$ii<$nvars} {incr ii} {
      #for all occurrences in event definition
      while {1} {
        set tt [lsearch -exact $cexp "\%$ii"]
        if {$tt!=-1} {
          #now replace %n with tt-th variable
          set cexp [lreplace $cexp $tt $tt $var($ii)]
#         puts "At $tt|$var($ii)|in|$cexp|"
#         puts $dbg "\nAt idx $tt in var($ii)|$var($ii)|in cexp|$cexp|"
        } else {
          break
        }
      }
    }
    set cexp [string trim $cexp \ ]
    #good debug but a lot of data >256K
#   puts $dbg "Subst evt|$cexp|"
#   puts "Subst evt|$cexp|"
#   puts "Hit any key";gets stdin getch;if {$getch=="q"} {exit}
    #also problem if subst is null {} inside parens and = condition
    #problem here if variable to be substituted contains [] eg procedure[trial]
    while {1} {
      set ppp [string first \{\} $cexp]
      if {$ppp==-1} {break}
#     puts "Expression contains nulls ie missing values, skip"
      set part2 [string range $cexp [expr $ppp+3] end]
      set cexp [string range $cexp 0 [expr $ppp-1]]
      append cexp "XXX $part2"
#     puts "New expression |$cexp|"
    }
    #kludge skip if [] present
    if {[string first \[ $cexp]==-1 && [string first \] $cexp]==-1} {
#     puts $dbg "Call Parser with|$cexp|"
#     gets stdin getch
      ##################### call to parser recursive proc###################
      set retval 0
      set prens 0
      set result [eval $cexp]
#     puts "Result=$result  Retval=$retval"
      ##################### call to parser recursive proc###################
      if {$result==1} {
        set absclk [lindex $varline $et]
        if {[regexp {^[0-9]} $absclk]==0} {
          puts $dbg "absclk non-num in data line at idx|$et|\n|$varline|"
          continue
        }
#       puts "et|$et|absclk|$absclk|"
#       gets stdin getch
        #generic output whatever is in output.nnn
        #CAUTION: temporary no run number
#       puts -nonewline $out "$evtid\t$runno"
        puts -nonewline $out "$evtid"
        for {set ii 0} {$ii<=$yy} {incr ii} {
          #if data not in output list (yet eg incomplete expt), missing value
          if {[expr $oidx($ii)]>=$nvars || $oidx($ii)==-1} {
            puts -nonewline $out "\t"
          } else {
            puts -nonewline $out "\t$var([expr $oidx($ii)])"
          }
        }
        puts $out ""
        #CAUTION: problem with multiple part trial which onsettime?
        #write out fractional volume:elim epvol.tcl step
        set rtime [format "%f" [expr $absclk-$runclk]]
        set rtime [format "%6.2f" [expr $rtime/2000.]]
        set rtime [string trimleft $rtime \ ]
        puts -nonewline $vol "$rtime "
#       puts -nonewline "$rtime "
#       puts "Hit any key";gets stdin getch;if {$getch=="q"} {exit}
        incr evtcntr
      } else {
#       puts $dbg "result=$result failed"
      }
    }
  }
  puts $vol "\n"
  puts "$evtid: Found $evtcntr\n"
  puts $sts "$evtid: Found $evtcntr\n"
  puts $dbg "$evtid: Found $evtcntr"
  puts $vol "$evtid: Found $evtcntr\n"
# puts "Hit any key, q to quit";gets stdin getch;if {$getch=="q"} {exit}
}
