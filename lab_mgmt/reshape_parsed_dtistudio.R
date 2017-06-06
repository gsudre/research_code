res_dir = '~/ayaka/'
files = dir(path = res_dir, pattern = 'parsed.csv$')
res = c()
for (f in files) {
  print(f)
  a = read.csv(sprintf('%s/%s', res_dir, f), row.names=1)
  print(dim(a))
  vals = a['FA', ]
  vals = cbind(vals, 3 * a['TR', ])  # MD
  vals = cbind(vals, a['eigval1', ]) # AD
  vals = cbind(vals, (a['eigval2', ] + a['eigval3', ])/2) # RD
  res = rbind(res, vals)
}
rownames(res) = files
rois = colnames(a)
header = c()
for (m in c('FA', 'MD', 'AD', 'RD')) {
  for (r in rois) {
    header = c(header, sprintf('%s_%s', m, r))
  }
}
colnames(res) = header
write.csv(res, file='~/tmp/results.csv')