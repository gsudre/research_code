set subj = 0121
set subj_folder = ~/tmp/${subj}.stop.results/gPPI_Gang/
# there are 4 runs
set nruns = 4
# number of time points per run in TR
set n_tp = 98
set TR = 2
# up-sample the data
set sub_TR = .1
# seed label
set sd = left_vlpfc
set condList = ( STG-correct STG-incorrect STI-correct STI-incorrect )

set mask_file = ~/tmp/${sd}_stop_mask+tlrc

mkdir $subj_folder
cd $subj_folder

# create Gamma impulse response function
waver -dt ${sub_TR} -GAM -peak 1 -inline 1@1 > GammaHR.1D

set run_length = `ccalc -i "${TR} * ${n_tp}"`
set nup = `ccalc -i "${TR} / ${sub_TR}"`
set up_run_length = `ccalc -i "${nup} * ${n_tp}"`
# for each run, extract seed time series, run deconvolution, and create interaction regressor
foreach cc (`count -digits 1 1 $nruns`)
    # get time series in the ROI for this particular run
   3dmaskave -mask $mask_file -quiet ../pb04.$subj.r0${cc}.scale+tlrc > Seed${cc}${sd}.1D
   # detrend time series. Time is in the rows, so we transpose the input
   3dDetrend -polort 2 -prefix SeedR${cc}${sd} Seed${cc}${sd}.1D\'
   # transpose it because 1dUpsample takes in time as a column
   1dtranspose SeedR${cc}${sd}.1D Seed_ts${cc}${sd}D.1D
   rm -f SeedR${cc}${sd}.1D
   1dUpsample $nup Seed_ts${cc}${sd}D.1D > Seed_ts${cc}${sd}.1D
   # Run deconvolution on the seed time series
   3dTfitter -RHS Seed_ts${cc}${sd}.1D -FALTUNG GammaHR.1D Seed_Neur${cc}${sd} 012 -1
   foreach cond ($condList)
      # get the timing for the given run of this condition
      head -${cc} ../stimuli/${subj}_${cond}.txt | tail -1 > tmp.1D
      # TR is 2000ms and there are 98 TRs per run. TR gets an event if at least 30% of the TR is is occupied by stimulus
      timing_tool.py -timing tmp.1D -tr ${sub_TR} -min_frac 0.3 -run_len $run_length -stim_dur 1 -timing_to_1D ${cond}${cc}${sd}.1D
      rm -f tmp.1D
      # interaction between the seed neural signal and the condition 1s
      1deval -a Seed_Neur${cc}${sd}.1D\' -b ${cond}${cc}${sd}.1D -expr 'a*b' > Inter_neu${cond}${cc}${sd}.1D
      # this is the interaction regressor
      waver -GAM -peak 1 -TR ${sub_TR} -input Inter_neu${cond}${cc}${sd}.1D -numout ${up_run_length} > Inter_hrf${cond}${cc}${sd}.1D
      # down-sample the interaction time series back to TR grids
      1dcat Inter_hrf${cond}${cc}${sd}.1D'{0..$('${nup}')}' > Inter_ts${cond}${cc}${sd}.1D
   end
end

# catenate the two regressors across runs
cat Seed_ts?${sd}D.1D > Seed_ts${sd}.1D
foreach cond ($condList)
  cat Inter_ts${cond}?${sd}.1D > Inter_ts${cond}${sd}.1D
end

# # re-run regression analysis by adding the two regressors
3dDeconvolve -input ../pb04.$subj.r*.scale+tlrc.HEAD                        \
    -censor ../censor_${subj}_combined_2.1D                                 \
    -polort 2                                                           \
    -num_stimts 15                                                       \
    -stim_times 1 ../stimuli/${subj}_STG-correct.txt 'BLOCK(1,1)'              \
    -stim_label 1 STG-correct                                            \
    -stim_times 2 ../stimuli/${subj}_STG-incorrect.txt 'BLOCK(1,1)'            \
    -stim_label 2 STG-incorrect                                          \
    -stim_times 3 ../stimuli/${subj}_STI-correct.txt 'BLOCK(1,1)'              \
    -stim_label 3 STI-correct                                            \
    -stim_times 4 ../stimuli/${subj}_STI-incorrect.txt 'BLOCK(1,1)'            \
    -stim_label 4 STI-incorrect                                          \
    -stim_file 5 ../motion_demean.1D'[0]' -stim_base 5 -stim_label 5 roll   \
    -stim_file 6 ../motion_demean.1D'[1]' -stim_base 6 -stim_label 6 pitch  \
    -stim_file 7 ../motion_demean.1D'[2]' -stim_base 7 -stim_label 7 yaw    \
    -stim_file 8 ../motion_demean.1D'[3]' -stim_base 8 -stim_label 8 dS     \
    -stim_file 9 ../motion_demean.1D'[4]' -stim_base 9 -stim_label 9 dL     \
    -stim_file 10 ../motion_demean.1D'[5]' -stim_base 10 -stim_label 10 dP  \
    -stim_file 11 Seed_ts${sd}.1D -stim_label 11 Seed    \
    -stim_file 12 Inter_ts${condList[1]}${sd}.1D -stim_label 12 PPI_${condList[1]}    \
    -stim_file 13 Inter_ts${condList[2]}${sd}.1D -stim_label 13 PPI_${condList[2]}    \
    -stim_file 14 Inter_ts${condList[3]}${sd}.1D -stim_label 14 PPI_${condList[3]}    \
    -stim_file 15 Inter_ts${condList[4]}${sd}.1D -stim_label 15 PPI_${condList[4]}    \
    -bout -rout                                                               \
    -tout -fout                                                               \
    -local_times                                                         \
    -GOFORIT 99                                                          \
    -allzero_OK                                                          \
    -jobs 3                                                              \
    -noFDR                                                               \
    -gltsym 'SYM: STI-correct -STG-correct' -glt_label 1                 \
        STI-correct_VS_STG-correct                                       \
    -gltsym 'SYM: STI-incorrect -STG-correct' -glt_label 2               \
        STI-incorrect_VS_STG-correct                                     \
    -gltsym 'SYM: STI-incorrect -STI-correct' -glt_label 3               \
        STI-incorrect_VS_STI-correct                                     \
    -errts errts.PPI.${sd}                                        \
    -bucket PPIstats.${sd}

