# Calculates slopes for thalamus variables
# load('/Volumes/Shaw/tmp/for_carly/DATA_1473.RData')
get_delta = function (d, ages) {
  # if we have too many NAs, return NA
  if (sum(is.na(d)) >= (length(d)-1)) {
    return(NA)
  }
  else {
    lm(d ~ ages)$coefficients[2]
  }
}

slopes_dtL_thamalus = c()
slopes_dtR_thamalus = c()
mrns = c()
library(parallel)
cl <- makeCluster(4)
cnt = 0
for (s in unique(gf_1473$PERSON.x)) {
  print(sprintf('%d of %d', cnt + 1, length(unique(gf_1473$PERSON.x))))
  idx = gf_1473$PERSON.x==s
  # proceed if we have more than one observation in the data
  if (sum(idx) >= 2) {
    subj_data = dtL_thalamus_1473[, idx]
    subj_ages = gf_1473[idx,]$AGESCAN
    slopes = parRapply(cl, subj_data, get_delta, subj_ages)
    slopes_dtL_thamalus = rbind(slopes_dtL_thamalus, slopes)
    subj_data = dtR_thalamus_1473[, idx]
    slopes = parRapply(cl, subj_data, get_delta, subj_ages)
    slopes_dtR_thamalus = rbind(slopes_dtR_thamalus, slopes)
    mrns = c(mrns, s)
  }
  cnt = cnt + 1
}
stopCluster(cl)

save(mrns, slopes_dtL_thamalus, slopes_dtR_thamalus, file='/Volumes/Shaw/tmp/for_carly/thalamus_slopes_1473.RData')