p = read.table('/scratch/sudregp/1080_rd.txt')  # just to get voxel coordinates
nvox = nrow(p)
b=p
data_dir = '/scratch/sudregp/prs/dti_voxels_rd_wnhaa_extendedfamID_lme_1kg9_cov_agePlusSex/PROFILES.0.1.profile/SX_HI/'
perms = list.files(path=data_dir, pattern="^perm*", include.dirs=T)
for (perm in perms) {
    if (!file.exists(sprintf('%s/pvals_%s.txt', data_dir, perm))) {
        print(perm)
        for (i in 1:nvox) {
        if (i %% 1000 == 0) {print(i)}
        fname = sprintf('%s/%s/v%05d.csv', data_dir, perm, i)
        d = read.csv(fname)
        p[i, 4] = 1-d$acme_p
        b[i, 4] = d$acme
        }
        write.table(p, file=sprintf('%s/pvals_%s.txt', data_dir, perm), row.names=F, col.names=F)
        write.table(b, file=sprintf('%s/betas_%s.txt', data_dir, perm), row.names=F, col.names=F)
    } else {
        print(sprintf('collected files for %s exist.', perm))
    }
}