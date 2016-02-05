# Creates time series for different ROIs
s=$1
cnt=0
while read roi; do 
    echo $roi $cnt
    mydir=/mnt/neuro/data_by_maskID/${s}/afni/${s}.rest.compCor.results
    3dmaskave -q -dball $roi 5 ${mydir}/errts.${s}.compCor+tlrc > ${s}_roi${cnt}.1D
    # mydir=/mnt/neuro/data_by_maskID/${s}/afni/${s}.rest.compCor.results
    # 3dmaskave -q -dball $roi 5 ${mydir}/errts.anaticor.${s}+tlrc > ${s}_roi${cnt}.1D
    let cnt=cnt+1
done < tlrc_seeds_targets_RAI.txt