#!/bin/sh
1dplot Resp_epiRT_scan_$1.1D &
1dplot ECG_epiRT_scan_$1.1D &
1dplot -xaxis 0:500:5:10 ECG_epiRT_scan_$1.1D & 
1dplot -xaxis 0:1500:5:10 Resp_epiRT_scan_$1.1D & 
