maskid=$1
thresh=(.01 .015 .02 .025 .05 .075 .1 .125 .15 .175 .2 .225 .25 .275 .3)
labels=(Caudate Putamen Thalamus Superior_Temporal_Gyrus Inferior_Parietal_Lobule Medial_Globus_Pallidus Lateral_Globus_Pallidus Medial_Frontal_Gyrus Superior_Occipital_Gyrus)

for scan in vid1 vid2 tfree1 tfree2; do
    logfile=/Users/sudregp/data/results/asl/log_${maskid}_${scan}.txt
    echo ================= > $logfile
    for t in ${thresh[@]}; do
        csh /Users/sudregp/research_code/asl/procPCASL.sh volreg.${scan}+orig.BRIK 2500 1500 redo $t | tee -a $logfile
        3dAllineate -base anat+tlrc -input volreg.${scan}_cbf+orig -1Dmatrix_apply volreg.${scan}_al_tlrc_mat.aff12.1D -prefix volreg.${scan}_cbf+tlrc -overwrite
        for h in left right; do
            for l in ${labels[@]}; do
                echo ::${h}:${l}:: >> $logfile
                3dmaskave -mask TT_Daemon:${h}:${l} volreg.${scan}_cbf+tlrc | tee -a $logfile
            done
        done
        echo ================= >> $logfile
    done
done