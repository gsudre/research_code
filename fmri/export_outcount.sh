#!/bin/bash
subj=$1
fname=/mnt/neuro/data_by_maskID/${subj}/afni/rest+orig
3dTcat -prefix ./tmp ${fname}"[3..$]" -overwrite
3dToutcount -automask -fraction -polort 3 -legendre tmp+orig > outcount.${subj}.1D
