# figure out the baseline scans. For 9 months, min_time_diff = .75
get_single_scans = function(data, min_time_diff=0, last_scan=F) {
    keep = vector()
    for (mrn in unique(data$MRN)) {
        idx = which(data$MRN == mrn)
        mrn_ages = data$age_at_scan[idx]
        if (length(mrn_ages) > 1 && diff(mrn_ages)[1] < min_time_diff) {
            cat(sprintf('ERROR: Scans for %d are not more than %.2f apart!',
                        mrn, min_time_diff))
        }
        keep = append(keep, idx[sort(mrn_ages, index.return=T, decreasing = last_scan)$ix[1]])
    }
    data = data[keep,]
    return (data)
}


# from https://sejohnston.com/2012/08/09/a-quick-and-easy-function-to-plot-lm-results-in-r/
ggplotRegression <- function (fit) {
    require(ggplot2)
    ggplot(fit$model, aes_string(x = names(fit$model)[2], y = names(fit$model)[1])) + 
    geom_point() +
    stat_smooth(method = "lm", col = "red") +
    labs(title = paste("Adj R2 = ",signif(summary(fit)$adj.r.squared, 5),
                        "Intercept =",signif(fit$coef[[1]],5 ),
                        " Slope =",signif(fit$coef[[2]], 5),
                        " P =",signif(summary(fit)$coef[2,4], 5)))
}