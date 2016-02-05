cond=STI-correct_VS_STI-incorrect_GLT
nv=/mnt/shaw/MR_behavioral/stop_task_analysis/whole_brain_analysis_w_mask/nv.txt
rem=/mnt/shaw/MR_behavioral/stop_task_analysis/whole_brain_analysis_w_mask/remitted.txt
per=/mnt/shaw/MR_behavioral/stop_task_analysis/whole_brain_analysis_w_mask/persistent.txt
mask=/mnt/shaw/MR_behavioral/stop_task_analysis/whole_brain_analysis_w_mask/group_level_mask+tlrc

N=''; while read p; do N=${N}' -dset 1 '/mnt/shaw/data_by_maskID/${p}/afni/${p}.stop.results/stats.${p}+tlrc'['${cond}'#0_Coef]'; done < $nv
P=''; while read p; do P=${P}' -dset 2 '/mnt/shaw/data_by_maskID/${p}/afni/${p}.stop.results/stats.${p}+tlrc'['${cond}'#0_Coef]'; done < $per
R=''; while read p; do R=${R}' -dset 3 '/mnt/shaw/data_by_maskID/${p}/afni/${p}.stop.results/stats.${p}+tlrc'['${cond}'#0_Coef]'; done < $rem
3dANOVA -levels 3 $N $P $R \
         -ftr group                 \
         -mean 1 nv                 \
         -mean 2 persistent                \
         -mean 3 remission                \
         -diff 1 2 NvsP                \
         -diff 2 3 PvsR                \
         -diff 1 3 NvsR                \
         -contr  1  1 -1 NPvsR         \
         -contr -1  1  1 NvsPR         \
         -contr  1 -1  1 NRvsP         \
         -mask $mask    \
         -bucket ANOVA