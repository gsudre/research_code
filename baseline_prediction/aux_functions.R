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
