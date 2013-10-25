dsm = 5
g1 = 'remission'
g2 = 'persistent'
gf = read.csv(sprintf('~/data/structural/gf_1473_dsm45_matched_on18_dsm%d_diff_2to1.csv', dsm))
eval(parse(text=sprintf('idx = gf$group==g1 | gf$group==g2', dsm, dsm)))
ages = array()
groups = array()
subjects = unique(gf[idx,]$subject)  # only look at subjects that obeyed previous criteria
cnt=1
for (subj in subjects) {
    good_subj_scans <- which((gf$subject == subj) & idx)
    subj_ages <- gf[good_subj_scans,]$age
    if ((min(subj_ages)<18) && (max(subj_ages) > 18)) {
        tmp_ages <- sort(subj_ages)
        age_base = tmp_ages[1]
        age_last = tail(tmp_ages, n=1)
        ages[cnt] = age_last-age_base
        eval(parse(text=sprintf('groups[cnt] = unique(as.character(gf[good_subj_scans,]$group))', dsm)))
        cnt = cnt+1
    }
}
print(t.test(ages ~ as.factor(groups), var.equal=T))