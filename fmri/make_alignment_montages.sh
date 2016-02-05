# Generates montages for each component of gRAICAR. Heavily based on @DriveAfni

output_dir=~/tmp/align/

PIF=montages    #A string identifying programs launched by this script
#Get a free line and tag programs from this script
NPB="-npb `afni -available_npb_quiet` -pif $PIF -echo_edu" 

while read s; do
    echo ${s}
    overlay=/mnt/shaw/data_by_maskID/${s}/afni/${s}.rest.example11.results/all_runs.${s}+tlrc
    underlay=/mnt/shaw/data_by_maskID/${s}/afni/${s}.rest.example11.results/anat_final.${s}+tlrc
    overlay=~/data/fmri/${s}/${s}.rest.example11.results/all_runs.${s}+tlrc
    underlay=~/data/fmri/${s}/${s}.rest.example11.results/anat_final.${s}+tlrc
    @Quiet_Talkers -pif $PIF   #Quiet previously launched programs
    afni $NPB -niml -yesplugouts -dset $underlay $overlay >& /dev/null &

    plugout_drive  $NPB                                               \
               -com 'OPEN_WINDOW A.axialimage keypress=space      \
                                 geom=+56+44 mont=10x5:3'          \
               -com 'SWITCH_UNDERLAY $underlay'                        \
               -com "SWITCH_OVERLAY $overlay"                        \
               -com 'SEE_OVERLAY +'                               \
               -com 'SET_XHAIRS OFF'                               \
               -com 'SET_THRESHNEW 0'                               \
               -com "SAVE_PNG axialimage ${output_dir}/${s}_axial.png" \
               -com 'QUIT'        \
               -quit
done < ~/data/fmri/joel_all.txt
