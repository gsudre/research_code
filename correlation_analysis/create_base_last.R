load('~/data/structural/GP_1473.RData')
load('~/data/structural/DATA_1473.RData')
gf_1473 = read.csv('~/data/structural/gf_1473_dsm45_matched_on18_dsm5_diff.csv')
fname_suffix = '_SA_QCCIVETlt35_QCSUBePASS_MATCHDIFF_on18_dsm5.csv'
brain_data = c('dt%s_thalamus_1473', 'dt%s_striatum_1473', 'dt%s_gp', 'dt%s_cortex_SA_1473')
brain_names = c('thalamus', 'striatum', 'gp', 'cortex')
for (g in c('NV', 'remission', 'persistent')) {
    print(g)
    idx = gf_1473$outcomedsm4==sprintf('"%s"', g)
    idx_base <- array(data=F,dim=length(idx))
    idx_last <- array(data=F,dim=length(idx))
    # get rid of scans that don't pass our QC or that haven't been matched
    idx = idx & (gf_1473$qc_civet<3.5 & gf_1473$qc_sub1=='"PASS"' & gf_1473$match_outcome==1)
    # find out all scans for each unique subject
    subjects = unique(gf_1473[idx,]$personx)  # only look at subjects that obeyed previous criteria
    for (subj in subjects) {
        good_subj_scans <- which((gf_1473$personx == subj) & idx)
        # only use subjects with one scan < 18 and another after 18
        ages <- gf_1473[good_subj_scans,]$agescan
        if ((min(ages)<18) && (max(ages) > 18)) {
            ages <- sort(ages, index.return=T)
            # makes the first scan true
            idx_base[good_subj_scans[ages$ix][1]] = T
            # makes the last scan true
            idx_last[tail(good_subj_scans[ages$ix], n=1)] = T
        }
    }
    idx_base = idx & idx_base
    idx_last = idx & idx_last
    
    cnt = 1
    for (i in brain_data) {
        cat('Working on', brain_names[cnt], '\n')
        for (h in c('L', 'R')) {
            eval(parse(text=sprintf('mytable=%s[,idx_base]', sprintf(i, h))))
            print(dim(mytable))
            write.csv(mytable,file=sprintf('~/data/structural/base_%s%s_%s%s',
                                           brain_names[cnt], h, g, fname_suffix))
            eval(parse(text=sprintf('mytable=%s[,idx_last]', sprintf(i, h))))
            print(dim(mytable))
            write.csv(mytable,file=sprintf('~/data/structural/last_%s%s_%s%s',
                                           brain_names[cnt], h, g, fname_suffix))
        }
        cnt = cnt + 1
    }
}
