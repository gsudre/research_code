matched_gf = read.csv('~/data/structural/gf_1473_matched_on18.csv')
idx <- matched_gf$group3=='"remission"' & matched_gf$match_outcome==1 # matching script already uses the QC parameters
# idx <- gf_1473$GROUP3=="remission" & gf_1473$QC_sub=="PASS" & gf_1473$QC_CIVET<3.5
idx_base <- array(data=F,dim=length(idx))
idx_last <- array(data=F,dim=length(idx))
# find out all scans for each unique subject
subjects = unique(gf_1473[idx,]$PERSON.x)  # only look at subjects that obeyed previous criteria
for (subj in subjects) {
    good_subj_scans <- which((gf_1473$PERSON.x == subj) & idx)
    # only use subjects with one scan < 18 and another after 18
    ages <- gf_1473[good_subj_scans,]$AGESCAN
    if ((min(ages)<18) && (max(ages) > 18)) {
        ages <- sort(ages, index.return=T)
        # makes the first scan true
        idx_base[good_subj_scans[ages$ix][1]] = T
        # makes the last scan true
        idx_last[tail(good_subj_scans[ages$ix], n=1)] = T
    }
}
mytable <- dtL_thalamus_1473[,idx & idx_last]
write.csv(mytable,file='~/data/structural/last_thalamusL_SA_remission_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_mt18.csv')
mytable <- dtL_striatum_1473[,idx & idx_last]
write.csv(mytable,file='~/data/structural/last_striatumL_SA_remission_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_mt18.csv')
mytable <- dtL_cortex_SA_1473[,idx & idx_last]
write.csv(mytable,file='~/data/structural/last_cortexL_SA_remission_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_mt18.csv')
mytable <- dtL_gp[,idx & idx_last]
write.csv(mytable,file='~/data/structural/last_gpL_SA_remission_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_mt18.csv')
mytable <- dtL_thalamus_1473[,idx & idx_base]
write.csv(mytable,file='~/data/structural/baseline_thalamusL_SA_remission_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_lt18.csv')
mytable <- dtL_striatum_1473[,idx & idx_base]
write.csv(mytable,file='~/data/structural/baseline_striatumL_SA_remission_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_lt18.csv')
mytable <- dtL_cortex_SA_1473[,idx & idx_base]
write.csv(mytable,file='~/data/structural/baseline_cortexL_SA_remission_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_lt18.csv')
mytable <- dtL_gp[,idx & idx_base]
write.csv(mytable,file='~/data/structural/baseline_gpL_SA_remission_QCCIVETlt35_QCSUBePASS_MATCHSCRIPT_lt18.csv')
