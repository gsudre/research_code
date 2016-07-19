# Creates phenotype files for SOLAR, using the output voxel-wise data
group = '3min'
nets = c(2, 5, 11, 4, 12, 6, 0) #0:15
fam_type = 'LE22'
for (net in nets) {
    gf_fname = sprintf('~/data/solar_paper_review/fmri_%s_melodicMasked_5comps_%s_noSingletons.csv', group, fam_type)
    data_fname = sprintf('~/data/solar_paper_review/%s_net%02d_%s_noSingletons.txt', group, net, fam_type)
    subjs_fname = sprintf('~/data/solar_paper_review/%s_noSingletons.txt', group, fam_type)

    cat(sprintf('Loading data net %d\n', net))
    brain = read.table(data_fname)
    gf = read.csv(gf_fname)
    subjs = read.table(subjs_fname)
    brain = cbind(subjs, t(brain))
    # only construct the header once
    if (length(header) == 0) {
        for (v in 1:(dim(brain)[2] - 1)) {
            header = c(header, sprintf('v%d', v))
        }
    }
    colnames(brain) = c('maskid', header)
    cat('Merging gf and brain data\n')
    data = merge(gf, brain, by.x='maskid', by.y='maskid')

    fam_str = sprintf('_%s', fam_type)

    out_fname = sprintf('~/data/solar_paper_review/phen_%s_net%02d%s_noSingletons.csv', group, net, fam_str)

    write.csv(data, file=out_fname, row.names=F, quote=F)
}
