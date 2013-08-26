# Adapted from proc, resulting form afni_proc. Calculates motion in subject's native space and spits out some results.
# Gustavo Sudre, 07/2013
 
set runs = (`count -digits 1 1 4`)

foreach run ( $runs )
    # register each volume to the base
    3dvolreg -verbose -zpad 1 -base stop_run4+orig'[97]' \
             -1Dfile dfile.r$run.1D -prefix rm.epi.volreg.r$run      \
             -cubic                                                  \
             -1Dmatrix_save mat.r$run.vr.aff12.1D                    \
             stop_run$run+orig
end

# make a single file of registration params
cat dfile.r*.1D > dfile_rall.1D

# create censor file motion_${subj}_censor.1D, for censoring motion 
1d_tool.py -infile dfile_rall.1D -set_nruns 4                           \
    -show_censor_count -censor_prev_TR                                  \
    -censor_motion 1 motion -overwrite

set mmean = `3dTstat -prefix - -mean motion_enorm.1D\' | & tail -n 1`
echo "average motion per TR = $mmean"

set mcount = `1deval -a motion_enorm.1D -expr "step(a-1)"      \
                        | awk '$1 != 0 {print}' | wc -l`
echo "num TRs above 1mm motion limit   : $mcount"

rm -f dfile* mat* mot* rm.*
