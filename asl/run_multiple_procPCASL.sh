fnum=2
logfile=/Users/sudregp/data/results/asl/log_1317_${fnum}.txt
#thresh=(.01 .015 .02 .025 .05 .075 .1 .125 .15 .175 .2 .225 .25 .275 .3)
thresh=(.02 .03 .04 .05 .06 .35 .46 .5)
labels=(Caudate Putamen Thalamus Superior_Temporal_Gyrus Inferior_Parietal_Lobule Medial_Globus_Pallidus Lateral_Globus_Pallidus Medial_Frontal_Gyrus Superior_Occipital_Gyrus)

echo ================= > $logfile
for t in ${thresh[@]}; do
    csh /Users/sudregp/research_code/asl/procPCASL.sh volreg${fnum}+orig.BRIK 2500 1500 redo $t | tee -a $logfile
    3dAllineate -base mprage+tlrc -input volreg${fnum}_cbf+orig -1Dmatrix_apply mat.${fnum}.warp.aff12.1D -prefix volreg${fnum}_cbf -overwrite
    for h in left right; do
        for l in ${labels[@]}; do
            echo ::${h}:${l}:: >> $logfile
            3dmaskave -mask TT_Daemon:${h}:${l} volreg${fnum}_cbf+tlrc | tee -a $logfile
        done
    done
    echo ================= >> $logfile
done