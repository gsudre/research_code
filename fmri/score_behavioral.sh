#!/bin/bash

tclsh extr.tcl $1
tclsh evt.tcl $1
tclsh split.tcl $1
bash gort.sh
bash ssrt.sh
cat stg.dbg sti.dbg > "$1"sum.txt
tclsh ssrt.tcl STG.rt
tclsh ssrt.tcl STI.rt
tclsh stdev.tcl STG.rt

mkdir $1
cp *.spt $1/
cp *.rt $1/
cp *.ssr $1/
cp *.ave $1/
cp stgstd.txt "$1"std.txt
mv $1std.txt $1/
mv $1sum.txt $1/
mv stgstd.txt $1/

tclsh ssrtstp.tcl
cp stgcalc.ssr "$1"stp.ssr
cp "$1"*.ssr $1/
rm *calc.ssr
rm *.ssr
rm *.sts
rm *.vol
rm *.dbg
rm *.fnd
rm *.fld
rm *.rt
rm *.ave
rm gort.sh
rm ssrt.sh
rm sum.stp
rm *e.txt
rm *.spt
rm titles
