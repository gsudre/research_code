# Checks the impact of QC in different brain metrics

df = read.csv('/Volumes/Shaw/longitudinal_anatomy/all_data_philip_update2_gs2.csv')

# we need to manually transform some metrics so that smaller is always better
df$mriqc_qi_2 = -log10(df$mriqc_qi_2)
df$mriqc_fber = -log10(df$mriqc_fber)
df$mriqc_cnr = -df$mriqc_cnr
df$mriqc_snr_total = -df$mriqc_snr_total

# qc metrics to use
qc_metrics = c('mriqc_qi_2', 'mriqc_fber', 'mriqc_cnr', 'mriqc_snr_total', 'mriqc_fwhm_avg', 'mriqc_efc',
               'civetqc_MASK_ERROR', 'civetqc_LEFT_INTER', 'civetqc_RIGHT_INTER', 'MPRAGE_QC')

# breaks in the data, where smaller is better, 0 to 100 (e.g. 10 = use top 10% of the data with highest quality)
# qbreaks = c(10, 25, 50, 75, 100)
qbreaks = c(5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 85, 90, 95, 100)

# brain_vars = c('freesurfer_crossPipe_Brain.Stem', 'freesurfer_crossPipe_lh_caudalmiddlefrontal_area')
brain_vars = colnames(df)[grepl('^freesurfer_crossPipe_', colnames(df))]

all_res = c()
for (roi in brain_vars) {
  print(roi)
  # results will be qbreaks by metric*3 + 2 (for roi and Q)
  res = as.data.frame(matrix(nrow = length(qbreaks), ncol = (length(qc_metrics)*3 + 2)))
  colnames(res) = c('roi', 'quantile', unlist(lapply(qc_metrics, function(x) c(sprintf('%s_n', x),
                                                          sprintf('%s_tstat', x),
                                                          sprintf('%s_pval', x)))))
  
  for (i in 1:length(qbreaks)) {
    res[i, 'quantile'] = qbreaks[i]
    res[i, 'roi'] = gsub('freesurfer_crossPipe_', '', roi)
    for (qc in qc_metrics) {
      thresh = quantile(df[, qc], probs=qbreaks[i]/100, na.rm=T)
      idx = which(df[, qc] <= thresh)  # just to deal with NAs
      # use covariates always in the end!!!
      fm_str = '%s ~ %s + AGESCAN + SEX'
      fit = lm(as.formula(sprintf(fm_str, roi, qc)), data=df[idx, ])
      # collecting results
      res[i, sprintf('%s_n', qc)] = length(idx)
      if (sum((rownames(summary(fit)$coefficients) == qc)) > 0) {
        res[i, sprintf('%s_tstat', qc)] = summary(fit)$coefficients[qc, 't value']
        res[i, sprintf('%s_pval', qc)] = summary(fit)$coefficients[qc, 'Pr(>|t|)']
      }
    }
  }
  all_res = rbind(all_res, res)
}
write.csv(all_res, file='~/tmp/qc_impact.csv', row.names = F)
