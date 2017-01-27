# families to plot
families = read.table('~/tmp/fams.txt')
families = unique(families)
library(kinship2)
# column with binary indicator (black is 1, white is zero)
mycol = 7
# remove the whitest and reddest colors
ped = read.csv('~/tmp/new_pedigree.csv')
for (f in 1:dim(families)[1]) {
    myfam = families[f, 1]
    cat(sprintf('Plotting family %d\n', myfam))
    idx = ped$famid==myfam
    ped2 = pedigree(ped[idx,]$id, ped[idx,]$fa, ped[idx,]$mo, ped[idx,]$sex, missid=0)
    vals = vector()
    # for each ID in the pedigree
    for (id in ped2$id) {
        vals = append(vals, ped[as.character(ped$id)==id, mycol])
     }
     pdf(sprintf('~/tmp/%d.pdf', myfam))
     # sx = rep('', length(vals))
     # plot(ped2, col=colors, affected=affected)
     plot(ped2, affected=vals, cex=.7)
     # title(sprintf('Family %d, phenotype %s', myfam, colnames(phe)[mycol]))
     title(sprintf('Family %d, phenotyped', myfam))
     dev.off()
}
