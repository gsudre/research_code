p = read.table('/scratch/sudregp/1080_rd.txt')
b=p
data_dir = '/scratch/sudregp/prs/dti_voxels_fa_wnhaa_extendedfamID_lme_1kg9_cov_agePlusSex/'
profiles = list.files(path=data_dir, pattern="^PROFILES*", include.dirs=T)
for (prof in profiles) {
  Ys = list.files(path=sprintf('%s/%s/', data_dir, prof), pattern="*", include.dirs=T)
  for (y in Ys) {
    print(c(prof, y))
    for (i in 1:12014) {
      if (i %% 1000 == 0) {print(i)}
      fname = sprintf('%s/%s/%s/v%05d.csv', data_dir, prof, y, i)
      d = read.csv(fname)
      p[i, 4] = 1-d$acme_p
      b[i, 4] = d$acme
    }
    write.table(p, file=sprintf('%s/%s_%s_pvals.txt', data_dir, prof, y), row.names=F, col.names=F)
    write.table(b, file=sprintf('%s/%s_%s_betas.txt', data_dir, prof, y), row.names=F, col.names=F)
  }
}