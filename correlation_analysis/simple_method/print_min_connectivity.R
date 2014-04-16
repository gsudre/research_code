get_min_connectivity <- function(other, time, hemi, pct, thresh, to_thalamus) {
    if (to_thalamus) {
        res = read.table(sprintf('~/data/results/simple/perm_conn_thresh%0.2f_%s%sthalamus%s_%s.txt',
                             thresh, other, hemi, hemi, time))
    } else {
        res = read.table(sprintf('~/data/results/simple/perm_conn_thresh%0.2f_thalamus%s%s%s_%s.txt',
                                 thresh, hemi, other, hemi, time))
    }
    tmp = sort(res[,1])
    # make sure I have at least 100 non-NA permutation values
    if (length(tmp)>100) {
        ci = tmp[ceiling(pct*length(tmp))]
    } else {
        ci = NA
    }
    return(ci)
}

other = 'cortex'
files = c('baseline', 'last', 'diff')
thresh = .5
hemi = 'R'
pct = .99
for (f in files) {
    ci = get_min_connectivity(other, f, hemi, pct, thresh, F)
    cat('Threshold:', thresh,'-> thalamus to', other, sprintf('(%s)', hemi), '\n')
    cat(f,':', ci,'\n')
    ci = get_min_connectivity(other, f, hemi, pct, thresh, T)
    cat('Threshold:', thresh,'->', other, sprintf('to thalamus (%s)', hemi), '\n')
    cat(f,':', ci,'\n')
}
