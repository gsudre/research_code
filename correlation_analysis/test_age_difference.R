dsm = 4
g1 = '"persistent"'
g2 = '"NV"'
gf_1473 = read.csv(sprintf('~/data/structural/gf_1473_dsm45_matched_on18_dsm%d_diff.csv', dsm))
eval(parse(text=sprintf('idx = gf_1473$outcomedsm%d==g1 | gf_1473$outcomedsm%d==g2', dsm, dsm)))
idx = idx & gf_1473$match_outcome==1
ages = array()
groups = array()
subjects = unique(gf_1473[idx,]$personx)  # only look at subjects that obeyed previous criteria
cnt=1
for (subj in subjects) {
    good_subj_scans <- which((gf_1473$personx == subj) & idx)
    subj_ages <- gf_1473[good_subj_scans,]$agescan
    if ((min(subj_ages)<18) && (max(subj_ages) > 18)) {
        tmp_ages <- sort(subj_ages)
        age_base = tmp_ages[1]
        age_last = tail(tmp_ages, n=1)
        ages[cnt] = age_last-age_base
        eval(parse(text=sprintf('groups[cnt] = unique(as.character(gf_1473[good_subj_scans,]$outcomedsm%d))', dsm)))
        cnt = cnt+1
    }
}
print(t.test(ages ~ as.factor(groups)))