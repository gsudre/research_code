#!/bin/sh
# Runs the rest of the compCor pipeline

subj=$1
subj_dir=/mnt/neuro/data_by_maskID/$subj/afni
old_pwd=`pwd`
# only go through if there is a compCor run
if [ -d ${subj_dir}/${subj}.rest.compCor.results ]; then
    cd ${subj_dir}/${subj}.rest.compCor.results
    # create WM + CSF mask
    3dcalc -a mask_WMe_resam+tlrc -b mask_CSFe_resam+tlrc -expr 'or(a,b)' -prefix mask_WMeORCSFe_resam+tlrc
    # select out censored TRs
    keep_trs=`1d_tool.py -infile X.xmat.1D -show_trs_uncensored encoded`
    # detrend the signal prior to blurring
    3dDetrend -prefix pb03.${subj}.r01.volreg.detrend -polort 3 pb03.${subj}.r01.volreg+tlrc"[$keep_trs]"
    # calculate the first 3 PCs
    3dpc -pcsave 3 -mask mask_WMeORCSFe_resam+tlrc -prefix ${subj}.WMCSFePC pb03.${subj}.r01.volreg.detrend+tlrc
    # regress out old X matrix (includes CSFe and motion), plus PCs and WM
    3dTfitter -polort -1 -RHS all_runs.$subj+tlrc"[$keep_trs]" -LHS X.xmat.1D WMeLocal_rall+tlrc ${subj}.WMCSFePC.1D -prefix stats.compCor.$subj -fitts fitts.compCor.$subj -errsum errts.compCor.$subj
else
    echo $subj has no compCor directory
fi
cd $old_pwd
