# Creates phenotype files for SOLAR, using the output voxel-wise data
group = '3min'
nets = c(0,2,4,6,7)
fam_type = ''

header = vector()
for (net in nets) {
    gf_fname = sprintf('~/data/solar_paper_noMeds/fmri_gf_%s.csv', group)
    # data_fname = sprintf('~/data/fmri_example11_all/%s_net%02d.txt', group, net)
    data_fname = sprintf('~/data/solar_paper_noMeds/%s_net%02d.txt', group, net)
    subjs_fname = sprintf('~/data/solar_paper_noMeds/%s.txt', group)

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

    if (fam_type != '') {
        idx = data$famType == fam_type
        data = data[idx,]
        fam_str = sprintf('_%s', fam_type)
    } else {
        fam_str = ''
    }
    # out_fname = sprintf('~/data/solar_paper_v2/phen_%s_net%02d%s.csv', group, net, fam_str)
    cat('Spitting out phenotype file\n')
    out_fname = sprintf('~/data/solar_paper_noMeds/redo/phen_%s_net%02d%s.csv', group, net, fam_str)
    write.csv(data, file=out_fname, row.names=F, quote=F)
}
