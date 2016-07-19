conds = c('STI-correct', 'STI-incorrect', 'correctVSincorrect')
bands = c('1to4', '4to8', '8to13', '13to30', '30to55', '65to100')
mask_fname = '/mnt/shaw/MEG_data/analysis/stop/source_volume_at_cross/nii_tlrc/mask.nii'
res_dir = '/mnt/shaw/MEG_data/analysis/stop/afni_results/red/'

n = 96

res.method = vector()
res.time = vector()
res.nvoxels=vector()
res.mintval=vector()

for (cond in conds) {
    for (band in bands) {
        for (clean in c('_clean')) {
            for (t in seq(0, 28)) {
                fname = sprintf('nvVSadhd_%s_DICSevoked_%s%s', cond, band, clean)
                cmd_str = sprintf('3dmaskdump -mask %s %s/%s_%d.nii[0] > ~/tmp/out.txt', mask_fname, res_dir, fname, t)
                system(cmd_str)
                out = read.table('~/tmp/out.txt')
                ts = out[, 4]
                ps = 2*pt(-abs(ts), df=n-1)
                cps = p.adjust(ps, method='fdr')
                good = cps < .05
                if (sum(good) > 0) {
                    mint = min(abs(ts[good]))
                } else {
                    mint = 0
                }
                res.method = c(res.method, fname)
                res.time = c(res.time, t)
                res.nvoxels = c(res.nvoxels, sum(good))
                res.mintval = c(res.mintval, mint)
            }
        }
    }
}
df = data.frame(method=res.method, time=res.time, nvoxels=res.nvoxels,
                mintval=res.mintval)
write.csv(df, file=sprintf('%s/nvVSadhd_fdr.csv', res_dir), row.names=F)

