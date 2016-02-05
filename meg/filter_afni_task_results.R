tests = c('inatt', 'hi', 'ssrt', 'inattWithNVs', 'hiWithNVs', 'ssrtWithNVs')
conds = c('STI-correct', 'STI-incorrect', 'correctVSincorrect')
covs = c('blank', 'base')
methods = c('dSPM', 'LCMV')
bands = c('1to4', '4to8', '8to13', '13to30', '30to55', '65to100')
mask_fname = '/mnt/shaw/MEG_data/analysis/stop/source_volume_at_cross/nii_tlrc/mask.nii'
res_dir = '/mnt/shaw/MEG_data/analysis/stop/afni_results/cross/'
for (test in tests) {
    if (length(grep('NV', test)) > 0) {
        n = 97
    } else {
        n = 52
    }
    print(test)
    print(n)
    res.method = vector()
    res.time = vector()
    res.nvoxels=vector()
    res.mintval=vector()
    for (cond in conds) {
        for (cov in covs) {
            for (method in methods) {
                for (clean in c('', '_clean')) {
                    for (t in seq(0, 28)) {
                        fname = sprintf('%s_%s_%s_%s%s', test, cond, method, cov, clean)
                        cmd_str = sprintf('3dmaskdump -mask %s %s/%s_%d.nii[1] > ~/tmp/out.txt', mask_fname, res_dir, fname, t)
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
    }

    for (cond in conds) {
        for (band in bands) {
            for (clean in c('', '_clean')) {
                for (t in seq(0, 28)) {
                    fname = sprintf('%s_%s_DICSevoked_%s%s', test, cond, band, clean)
                    cmd_str = sprintf('3dmaskdump -mask %s %s/%s_%d.nii[1] > ~/tmp/out.txt', mask_fname, res_dir, fname, t)
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
    write.csv(df, file=sprintf('%s/%s_fdr.csv', res_dir, test), row.names=F)
}

