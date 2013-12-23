other = 'striatum'
files = c('diff')
thresh = .5
hemi = 'L'
ci = vector(mode='numeric',length=length(files))
cat('Threshold:', thresh,'-> thalamus to', other, sprintf('(%s)', hemi), '\n')
for (f in 1:length(files)) {
    res = read.table(sprintf('~/data/results/simple/perm_conn_thresh%0.2f_thalamus%s%s%s_%s.txt',
                 thresh, hemi, other, hemi, files[f]))
    tmp = sort(res[,1])
    # make sure I have at least 100 non-NA permutation values
    if (length(tmp)>100) {
        ci[f] = tmp[ceiling(.99*length(tmp))]
    } else {
        ci[f] = NA
    }
    cat(files[f],':',ci[f],'\n')
}
