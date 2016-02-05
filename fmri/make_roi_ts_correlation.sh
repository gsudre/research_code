# Creates correlation maps for different ROIs
s=$1
cnt=0
while read roi; do 
    echo $roi $cnt
    # mydir=/mnt/neuro/data_by_maskID/${s}/afni/${s}.rest.compCor.results
    # 3dmaskave -q -dball $roi 5 ${mydir}/errts.${s}.compCor+tlrc > ${s}_roi${cnt}.1D
    # 3dTcorr1D -prefix corr_${s}_${cnt} -mask ${mydir}/brainmask+tlrc ${mydir}/errts.${s}.compCor+tlrc ${s}_roi${cnt}.1D
    mydir=/mnt/neuro/data_by_maskID/${s}/afni/${s}.rest.withPhysio.results
    3dmaskave -q -dball $roi 5 ${mydir}/errts.anaticor.${s}+tlrc > ${s}_roi${cnt}.1D
    3dTcorr1D -prefix corr_${s}_${cnt} -mask ${mydir}/mask_group+tlrc ${mydir}/errts.anaticor.${s}+tlrc ${s}_roi${cnt}.1D
    3dcalc -prefix Zcorr_${s}_${cnt} -a corr_${s}_${cnt}+tlrc -expr "atanh(a)"
    let cnt=cnt+1
done < tlrc_seeds_targets_RAI.txt