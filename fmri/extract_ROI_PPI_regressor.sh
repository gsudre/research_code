#!/bin/bash
# Written by Gustavo Sudre, 01/2015. Adapted from Joahanna Darko's script.

subj=0498
subj_dir=~/tmp/${subj}/afni/${subj}.stop.results/
mask_dir=~/tmp/masks/
# waver -dt .1 -GAM -inline 1@1 > masks/GammaHRF.1D
gamma_1d=~/tmp/masks/GammaHRF.1D
out_dir=${subj_dir}/gPPI
# upsampled TR
up_tr=0.1
nruns=4
nup=20  # TR / $up_tr
runTRs=(98 98 98 98)
# make sure a file called ROI_stop_mask exist for each of those ROIs in mask_dir. If not, do something like: 3dcalc -a 'TT_Daemon:l:amygdala' -expr 'step(a)' -prefix ~/tmp/junk and then 3dresample -overwrite -dxyz 3.5 3.5 3.5 -prefix amygdala_stop_mask -inset junk+tlrc
# rois=(brodmannArea44 brodmannArea45 brodmannArea47 putamen accumbens caudate brodmannArea24 brodmannArea32 brodmannArea33)
rois=(amygdala)
conditions=(STG-correct STG-incorrect STI-correct STI-incorrect)

# # check that the basic analysis for the subject has happened
# if [ ! -d $subj_dir ]; then
#     echo 'Could not find directory ${subj_dir}. Exiting...'
#     exit
# fi

# # check that we have a mask for each of the specified seed ROIs.
# for r in ${rois[@]}; do
#     mask_file=${mask_dir}/${r}_stop_mask+tlrc.HEAD
#     if [ ! -e $mask_file ]; then
#         echo 'Could not find mask for ROI ${r}. Exiting...'
#         exit
#     fi
# done

# # check that GammaHRF.1D exists
# if [ ! -e $gamma_1D ]; then
#     echo 'Could not find gamma 1D file. Exiting...'
#     exit
# fi

mkdir $out_dir

# create start and stop lists per run, storing the beginning and end of each run in the upsampled scale
run_start=()
run_end=()
start=0
for r in `count -digits 1 1 $nruns`; do 
   run_start+=( $start )
   rend=`ccalc -i "$start + ${runTRs[$r-1]} * $nup - 1"`
   run_end+=( $rend )
   start=`ccalc -i $rend+1`
done

# create upsampled timing files for all runs and for each individual run
for c in ${conditions[@]}; do
    # TR is 2000ms and there are 98 TRs per run. TR gets an event if at least 30% of the TR is is occupied by stimulus
    timing_tool.py -timing ${subj_dir}/stimuli/${subj}_${c}.txt -tr ${up_tr} -min_frac 0.3 -run_len 196 -stim_dur 1 -timing_to_1D ${out_dir}/${c}.upsam.1D

    for r in `count -digits 1 1 $nruns`; do
        cfile=${out_dir}/${c}.r${r}.upsam.1D
        # sed is 1-based
        let s0=${run_start[$r-1]}+1
        let sn=${run_end[$r-1]}+1
        # this sed command does the same as the 1dcat command in the original script
        sed -n ${s0},${sn}p ${out_dir}/${c}.upsam.1D > ${cfile}
    done
done

# then, for each ROI
for roi in ${rois[@]}; do
  mask_file=${mask_dir}/${roi}_stop_mask+tlrc
  for run in `count -digits 1 1 $nruns`; do
      # extract PPI regressors for each of the specified ROIs
      3dmaskave -quiet -mask ${ROIdir}/${mask_file} ${subj_dir}/pb04.${subj}.r0${run}.scale+tlrc > ${out_dir}/${roi}.run${run}.seed.1D

      # upsample the TRs because stimuli are not TR locked
      3dDetrend -overwrite -polort 2 -prefix ${roi}.run${run}.seed.dt_row.1D ${out_dir}/${roi}.run${run}.seed.1D\'
      1dtranspose ${roi}.run${run}.seed.dt_row.1D ${out_dir}/${roi}.run${run}.seed.dt.1D
      rm ${roi}.run${run}.seed.dt_row.1D      
      1dUpsample $nup ${out_dir}/${roi}.run${run}.seed.dt.1D > ${out_dir}/${roi}.run${run}.seed.dt.upsam.1D 

      # deconvolve upsampled seed roi time series with gamma variate HRF
      3dTfitter -RHS ${out_dir}/${roi}.run${run}.seed.dt.upsam.1D -FALTUNG ${gamma_1d} rm.temp.1D 012 -2 -l2lasso -6     
      1dtranspose rm.temp.1D > ${out_dir}/${roi}.run${run}.seed.dt.upsam.deconv.1D  
      rm rm.temp.1D

      # reconvolve interaction term with gamma HRF to isiolate neural response to the stimulus
      for cond in ${conditions[@]}; do
        cfile=${out_dir}/${cond}.r${run}.upsam.1D
        dfile=${out_dir}/${roi}.run${run}.seed.dt.upsam.deconv.1D
        bfile=${out_dir}/${roi}.${cond}.run${run}.PPI.upsam.1D
        wfile=${out_dir}/${roi}.${cond}.run${run}.PPI.upsam.reconv.1D
        nt=`ccalc -i ${run_end[$run-1]}-${run_start[$run-1]}+1`
        1deval -a ${dfile} -b ${cfile} -expr 'a*b' > ${bfile}
        waver -GAM -peak 1 -TR $up_tr -input ${bfile} -numout $nt > ${wfile}
      done
  done

  # detrend the ROI timeseries for the entire run
  cat ${out_dir}/${roi}.run*.seed.1D > ${out_dir}/${roi}.seed.1D
  3dDetrend -overwrite -polort 2 -prefix ${roi}.seed.dt_row.1D ${out_dir}/${roi}.seed.1D\'
  1dtranspose ${roi}.seed.dt_row.1D ${out_dir}/${roi}.seed.dt.1D
  rm ${roi}.seed.dt_row.1D

  # downsample interaction term to original TR resolution
  for cond in ${conditions[@]}; do
    cat ${out_dir}/${roi}.${cond}.run*.PPI.upsam.reconv.1D > ${out_dir}/${roi}.${cond}.rall.PPI.upsam.reconv.1D
    1dcat ${out_dir}/${roi}.${cond}.rall.PPI.upsam.reconv.1D"{0..\$($nup)}" > ${out_dir}/${roi}.${cond}.rall.PPI.reconv.1D
  done
done

# use ${roi}.${cond}.rall.PPI.reconv.1D as PPI regressor in future regression analysis!

