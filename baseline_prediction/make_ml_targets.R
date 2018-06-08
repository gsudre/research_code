sx = read.csv('~/data/baseline_prediction/clinical_long_06072018.csv')
df = data.frame(MRN = unique(sx$MRN))


outcome = c()
slopes = c()
for (s in df$MRN) {
  subj_clin = sx[sx$MRN == s, ]
  res = sort(subj_clin$age_clinical, index.return=T)
  subj_clin = subj_clin[res$ix,]
  # now we're sorted based on age of clinical
  
  # Figure out remitted and persistent
  if (subj_clin[1, 'SX_inatt'] >= 6 || subj_clin[1, 'SX_hi'] >= 6) {
    if (subj_clin[nrow(subj_clin), 'SX_inatt'] >= 6 || subj_clin[nrow(subj_clin), 'SX_hi'] >= 6) {
      outcome = c(outcome, 'persistent')
    } else {
      outcome = c(outcome, 'remission')
    }
  } else {
    outcome = c(outcome, 'NV')
  }
  
  # construct SX slopes
  fit_inatt = lm(SX_inatt ~ age_clinical, data = subj_clin)
  fit_hi = lm(SX_hi ~ age_clinical, data = subj_clin)
  slopes = rbind(slopes, c(coefficients((fit_inatt))['age_clinical'], coefficients((fit_hi))['age_clinical']))
}
df$outcome = outcome
df$slope_inatt = slopes[, 1]
df$slope_hi = slopes[, 2]

write.csv(df, file='~/data/baseline_prediction/clinical_targets_06082018.csv', row.names=F)