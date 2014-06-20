# Reports important information about TRs censored so one can put it in a spreadsheet

subjects_file=$1
mot_limit=0.2
out_limit=0.1

old_pwd=`pwd`
echo "Mask ID, TRs above motion limit,TRs above outlier limit,TRs censored,Fraction of TRs censored,Pipeline successfull"
while read subj; do 
    res_dir=/mnt/neuro/data_by_maskID/${subj}/afni/${subj}.rest.regressingOutPhysio.results
    enorm_dset=motion_${subj}_enorm.1D
    censor_dset=censor_${subj}_combined_2.1D

    cd $res_dir
    mcount=`1deval -a $enorm_dset -expr "step(a-$mot_limit)"      \
                            | awk '$1 != 0 {print}' | wc -l`
    # echo "num TRs above mot limit   : $mcount"

    ocount=`1deval -a outcount_rall.1D -expr "step(a-$out_limit)"      \
                            | awk '$1 != 0 {print}' | wc -l`
    # echo "num TRs above out limit   : $ocount"

    nruns=( `1d_tool.py -infile X.xmat.1D -show_num_runs` )
    trs=( `1d_tool.py -infile X.xmat.1D -show_tr_run_counts trs_no_cen` )
    # echo "num runs found            : $nruns"
    # echo "num TRs per run           : $trs"

    ntr_censor=`cat $censor_dset | grep 0 | wc -l`
    sfrac=`ccalc $ntr_censor/$trs`
    # echo "TRs censored              : $ntr_censor"
    # echo "censor fraction           : $sfrac"

    if [ -e ${res_dir}/\@ss_review_driver ]; then
        completed=1
    else
        completed=0
    fi

    echo "${subj},${mcount},${ocount},${ntr_censor},${sfrac},${completed}"
done < $subjects_file

cd $old_pwd
