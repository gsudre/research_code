# Creates phenotype files for SOLAR, using the output voxel-wise data
group = 'mean'
mode = c('fa', 'ad', 'rd')
fam_type = 'nuclear'
for (m in mode) {
    gf_fname = sprintf('~/data/solar_paper_v2/dti_%s_phenotype_cleanedWithinTract3sd_adhd_nodups_extendedAndNuclear_mvmt_pctMissingSE10_FAbt2.5.csv', group)
    data_fname = sprintf('~/data/dti_voxelwise/dti_%s.txt', m)
    subjs_fname = '~/data/dti_voxelwise/subjs.txt'

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
    data = merge(gf, brain, by.x='mask.id', by.y='maskid')

    if (fam_type != '') {
        idx = data$famType == fam_type
        data = data[idx,]
        fam_str = sprintf('_%s', fam_type)
    } else {
        fam_str = ''
    }
    out_fname = sprintf('~/data/solar_paper_v2/phen_%s_dti_%s%s.csv', group, m, fam_str)
    write.csv(data, file=out_fname, row.names=F, quote=F)
}
