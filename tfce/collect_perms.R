mode = 'vox' # 'vox' or 'tfce'
iter = 3
res_name = 'pairwise'
path = sprintf('~/data/results/tfce/perms%d/', iter)
if (mode=='tfce') {
    fname = sprintf('~/data/results/tfce/%s_tfce.txt', res_name)
    pattern = 'tfce.txt$' # ends in tfce
} else {
    fname = sprintf('~/data/results/tfce/%s.txt', res_name)
    pattern = '[0-9].txt$' # ends in a number
}
files = list.files(path, pattern=pattern)
nperms = length(files)
nvoxels = 80689
null_dist_corr = vector(length=nperms) 
ps = vector(length=nvoxels, mode='integer')
results = read.table(fname)
out = results[,1:4]
results = as.matrix(results[,4:dim(results)[2]])
for (f in 1:nperms) {
    cat(f, '/', nperms, '\n')
    data = read.table(sprintf("%s/%s", path, files[f]))
    data = as.matrix(data[,4:dim(data)[2]])
    null_dist_corr[f] = max(data)
    idx = data > results 
    ps[idx] = ps[idx] + 1
}
ps = ps/nperms
out[,4] = 1-ps
fname = sprintf('~/data/results/tfce/%s_%s_p.txt', res_name, mode)
write.table(out, file=fname, col.names=F, row.names=F)
corrps = ps  # just initializing it
for (v in 1:nvoxels) {
    corrps[v] = sum(null_dist_corr > results[v])/nperms
}
out[,4] = 1-corrps
fname = sprintf('~/data/results/tfce/%s_%s_corrp.txt', res_name, mode)
write.table(out, file=fname, col.names=F, row.names=F)