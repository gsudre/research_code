dsm = 5
g1 = 'remission'
g2 = 'persistent'
gf = read.csv(sprintf('~/data/structural/gf_1473_dsm45_matched_on18_dsm5_diff_2to1_v2.csv', dsm))
idx = gf$group==g1 | gf$group==g2
age_diff = array()
age_base = array()
age_fu = array()
groups = array()
subjects = unique(gf[idx,]$subject)  # only look at subjects that obeyed previous criteria
cnt=1
for (subj in subjects) {
    good_subj_scans <- which((gf$subject == subj) & idx)
    subj_ages <- gf[good_subj_scans,]$age
    if ((min(subj_ages)<18) && (max(subj_ages) > 18)) {
        tmp_ages <- sort(subj_ages)
        age_base[cnt] = tmp_ages[1]
        age_fu[cnt] = tail(tmp_ages, n=1)
        age_diff[cnt] = age_fu[cnt]-age_base[cnt]
        groups[cnt] = unique(as.character(gf[good_subj_scans,]$group))
        cnt = cnt+1
    }
}
print(t.test(age_base ~ as.factor(groups), var.equal=T))
print(t.test(age_fu ~ as.factor(groups), var.equal=T))
print(t.test(age_diff ~ as.factor(groups), var.equal=T))