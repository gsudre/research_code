# Generates montages for each component of gRAICAR. Heavily based on @DriveAfni

output_dir=/Users/sudregp/data/graicar/adults
report_dir=${output_dir}/rsFMRI_webreport_afni
maps_dir=${output_dir}/compMaps

# make a backup of the webreport folder
if [ ! -d $report_dir ]; then
    cp -r ${output_dir}/rsFMRI_webreport $report_dir
fi

PIF=gRAICAR_montages    #A string identifying programs launched by this script
#Get a free line and tag programs from this script
NPB="-npb `afni -available_npb_quiet` -pif $PIF -echo_edu" 

for c in {1..31}; do
    echo ${c}
    fname=$(printf 'comp%03d.nii.gz' $c)
    @Quiet_Talkers -pif $PIF   #Quiet previously launched programs
    afni $NPB -niml -yesplugouts -dset /Applications/afni/TT_N27+tlrc ${maps_dir}/${fname}  >& /dev/null &

    plugout_drive  $NPB                                               \
               -com 'OPEN_WINDOW A.axialimage keypress=space      \
                                 geom=+56+44 mont=10x5:3'          \
               -com 'SWITCH_UNDERLAY TT_N27'                        \
               -com "SWITCH_OVERLAY ${fname}"                        \
               -com 'SEE_OVERLAY +'                               \
               -com 'SET_XHAIRS OFF'                               \
               -com 'SET_THRESHNEW 0'                               \
               -com "SAVE_PNG axialimage ${report_dir}/map_AC_nothresh${c}.png"        \
               -com 'SET_FUNC_PERCENTILE +'                 \
               -com 'SET_THRESHNEW 0.95'                               \
               -com "SAVE_PNG axialimage ${report_dir}/map_AC${c}.png"        \
               -com 'QUIT'        \
               -quit
done
