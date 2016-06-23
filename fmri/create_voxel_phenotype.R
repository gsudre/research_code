# Creates phenotype files for SOLAR, using the output voxel-wise data
group = '3min'
nets = c(2, 5, 11, 4, 12, 6, 0) #0:15
fam_type = 'adults'
for (net in nets) {
    gf_fname = sprintf('~/data/solar_paper_v2/fmri_%s_melodicMasked_5comps_%s.csv', group, fam_type)
    # data_fname = sprintf('~/data/fmri_example11_all/%s_net%02d.txt', group, net)
    # data_fname = sprintf('~/data/test_full_grid_fmri/%s_net%02d.txt', group, net)
    data_fname = sprintf('~/data/solar_paper_v2/nifti/adults_children/%s_net%02d_%s.txt', group, net, fam_type)
    subjs_fname = sprintf('~/data/fmri_example11_all/%s_%s.txt', group, fam_type)

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

    # if (fam_type != '') {
    #     idx = data$famType == fam_type
    #     data = data[idx,]
    #     fam_str = sprintf('_%s', fam_type)
    # } else {
    #     fam_str = ''
    # }
    fam_str = sprintf('_%s', fam_type)

    out_fname = sprintf('~/data/solar_paper_v2/nifti/adults_children/phen_%s_net%02d%s.csv', group, net, fam_str)
    # out_fname = sprintf('~/data/solar_paper_v2/phen_%s_net%02d_full%s.csv', group, net, fam_str)
    write.csv(data, file=out_fname, row.names=F, quote=F)
}
