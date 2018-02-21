# families to plot
families = read.table('~/tmp/unique_famids.txt')
families = unique(families)
library(kinship2)
# column with binary indicator (black is 1, white is zero)
mycol = 8
ped = read.csv('/Volumes/Shaw/pedigrees/master/pedigree_20180112.csv')
for (f in 1:dim(families)[1]) {
    myfam = families[f, 1]
    cat(sprintf('Plotting family %d\n', myfam))
    idx = ped$FAMID==myfam
    ped2 = pedigree(ped[idx,]$ID, ped[idx,]$FA, ped[idx,]$MO, ped[idx,]$sex, missid=0)
    vals = vector()
    ids = vector()
    # for each ID in the pedigree
    for (id in ped2$id) {
        idx = as.character(ped$ID)==id
        vals = append(vals, ped[idx, mycol])
        # if (as.character(ped[idx,]$code) != '') {
        #     my_str = sprintf('%s\n(%d)', ped[idx,]$code, ped[idx,]$age)
        if (as.character(ped[idx,]$first_name) != '') {
            my_str = sprintf('%s\n%s (%d)', ped[idx,]$first_name,
                                            ped[idx,]$last_name,
                                            ped[idx,]$age)
        } else {
            my_str = '' #sprintf('%s', ped[idx,]$name)
        }
        ids = append(ids, my_str)
     }
     pdf(sprintf('/Volumes/Shaw/pedigree_trees/20180112/name_age_dx/%d.pdf', myfam))
     # sx = rep('', length(vals))
     # plot(ped2, col=colors, affected=affected)
     plot(ped2, affected=vals, cex=.4, id=ids)
     # title(sprintf('Family %d, phenotype %s', myfam, colnames(phe)[mycol]))
     title(sprintf('Family %d, ADHD DX', myfam))
     dev.off()
}
