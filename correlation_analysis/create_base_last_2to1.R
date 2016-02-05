dsm = 5
load(sprintf('~/data/structural/all_data_gf_1473_dsm%d_matchedDiff_on18_2to1.RData', dsm))
gf = read.csv(sprintf('~/data/structural/gf_1473_dsm45_matched_on18_dsm%d_diff_2to1.csv', dsm))
fname_suffix = '_SA_QCCIVETlt35_QCSUBePASS_MATCHDIFF_on18_dsm5_2to1.csv'
brain_data = c('thalamusL', 'thalamusR', 'striatumL', 'striatumR',
               'gpL', 'gpR')
for (g in c('NV', 'remission', 'persistent')) {
    print(g)
    idx = gf$group==sprintf('%s', g)
    # find out all scans for each unique subject
    subjects = unique(gf[idx,]$subject)  # only look at subjects that obeyed previous criteria
    for (subj in subjects) {
        good_subj_scans <- which((gf$subject == subj) & idx)
        # only use subjects with one scan < 18 and another after 18
        ages <- gf[good_subj_scans,]$age
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
    
    for (i in brain_data) {
        cat('Working on', i, '\n')
        eval(parse(text=sprintf('mytable=%s[,idx_base]', i)))
        print(dim(mytable))
        write.csv(mytable,file=sprintf('~/data/structural/base_%s_%s%s',
                                       i, g, fname_suffix))
        eval(parse(text=sprintf('mytable=%s[,idx_last]', i)))
        print(dim(mytable))
        write.csv(mytable,file=sprintf('~/data/structural/last_%s_%s%s',
                                       i, g, fname_suffix))
    }
}
