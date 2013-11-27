getMeds <- function(subjs, ages) {
    meds = vector(mode='logical', length=length(subjs))
    gf = read.csv('~/data/structural/gf_1473_dsm45_cleanMeds.csv')
    for (i in 1:length(subjs)) {
        # once we find one of the rows for the subject, we have all the info there.
        idx = which(gf$PERSON==subjs[i])[1]
        # we first find out which scan that age corresponds to
        scanNum = which(gf[idx,46:51]==ages[i])
        if (length(scanNum)==0) {
#             cat('Error: could not find age',ages[i],'for',subjs[i],'\n')
            meds[i] = F
        }
        else {
            # then, check if that scan was medicated or not
            meds[i] = gf[idx,26+scanNum-1]==1
            if (is.na(meds[i])) {
                meds[i] = F
            }
        }
    }
    return(meds)
}

# Run macacc_massage_data_matched_diff.R and compile_baseline.R first!

# check is baseline results change with meds
adhd_subjs = gfBase[gfBase$DX=='ADHD',]$PERSON.x
adhd_ages = gfBase[gfBase$DX=='ADHD',]$AGESCAN
adhd_meds = getMeds(adhd_subjs, adhd_ages)
cat(sprintf('%g / %g (%.2f) ADHD baseline subjects on meds\n', 
            sum(adhd_meds), length(adhd_subjs), sum(adhd_meds)/length(adhd_subjs)))

# check the baseline/FU data
gf = read.csv('~/data/structural/gf_1473_dsm45_matched_on18_dsm5_diff_2to1_v2.csv')
per_subjs = gf[gf$group=='persistent',]$subject
per_ages = gf[gf$group=='persistent',]$age
perB_meds = getMeds(per_subjs[seq(1,length(per_subjs),2)], per_ages[seq(1,length(per_subjs),2)])
cat(sprintf('%g / %g (%.2f) persistent baseline subjects on meds\n', 
            sum(perB_meds), length(per_subjs)/2, sum(perB_meds)/(length(per_subjs)/2)))
perF_meds = getMeds(per_subjs[seq(2,length(per_subjs),2)], per_ages[seq(2,length(per_subjs),2)])
cat(sprintf('%g / %g (%.2f) persistent FU subjects on meds\n', 
            sum(perF_meds), length(per_subjs)/2, sum(perF_meds)/(length(per_subjs)/2)))

rem_subjs = gf[gf$group=='remission',]$subject
rem_ages = gf[gf$group=='remission',]$age
remB_meds = getMeds(rem_subjs[seq(1,length(rem_subjs),2)], rem_ages[seq(1,length(rem_subjs),2)])
cat(sprintf('%g / %g (%.2f) remission baseline subjects on meds\n', 
            sum(remB_meds), length(rem_subjs)/2, sum(remB_meds)/(length(rem_subjs)/2)))
remF_meds = getMeds(rem_subjs[seq(2,length(rem_subjs),2)], rem_ages[seq(2,length(rem_subjs),2)])
cat(sprintf('%g / %g (%.2f) remission FU subjects on meds\n', 
            sum(remF_meds), length(rem_subjs)/2, sum(remF_meds)/(length(rem_subjs)/2)))