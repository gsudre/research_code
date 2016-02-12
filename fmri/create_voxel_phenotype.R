# Creates phenotype files for SOLAR, using the output voxel-wise data
group = '3min'
nets = 0:15
for (net in nets) {
    gf_fname = sprintf('~/data/solar_paper_v2/fmri_%s_melodicMasked_5comps.csv', group)
    data_fname = sprintf('~/data/fmri_example11_all/%s_net%02d.txt', group, net)
    subjs_fname = sprintf('~/data/fmri_example11_all/%s.txt', group)

    cat('Loading data\n')
    brain = read.table(data_fname)
    gf = read.csv(gf_fname)
    subjs = read.table(subjs_fname)
    brain = cbind(subjs, t(brain))
    header = vector()
    for (v in 1:(dim(brain)[2] - 1)) {
        header = c(header, sprintf('v%d', v))
    }
    colnames(brain) = c('maskid', header)
    data = merge(gf, brain, by.x='maskid', by.y='maskid')

    out_fname = sprintf('~/data/solar_paper_v2/phen_%s_net%02d.csv', group, net)
    write.csv(data, file=out_fname, row.names=F, quote=F)
}
