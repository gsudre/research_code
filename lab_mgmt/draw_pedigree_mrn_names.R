families = read.table('~/data/pedigrees/famids.txt')[,1]
families = unique(families)
library(kinship2)
library(RColorBrewer)
mycol = 2
pal = brewer.pal(9, "Reds")
# remove the whitest and reddest colors
pal = pal[2:8]
# expand the palette so that we have enough colors
ped = read.csv('~/data/pedigrees/pedigree_20200824.csv')
phe = read.csv('~/data/pedigrees/pheno.csv')
for (myfam in families) {
    cat(sprintf('Plotting family %d\n', myfam))
    idx = ped$FAMID==myfam
    ped2 = pedigree(ped[idx,]$ID, ped[idx,]$FA, ped[idx,]$MO, ped[idx,]$SEX,
                    missid=0)
    affected = vector()
    vals = vector()
    sx = vector()
    for (id in ped2$id) {
        idx = as.character(phe$ID)==id
        # if we found phenotype for this ID
        if (sum(idx) > 0) {
            sx_str = sprintf('%s\n%s\n(%s)\n%.0f yo', phe[idx,]$first.name,
                             phe[idx,]$last.name, id,
                             as.numeric(phe[idx,]$age_today))
        }
        else {
            sx_str = sprintf('%s', id)
        }
        sx = c(sx, sx_str)  
    }
    pdf(sprintf('~/data/pedigrees/new_trees/%d.pdf', myfam))
    plot(ped2, symbolsize=1, id=sx, cex=.4, mar = c(4.1, 2.2, 4.1, 2.2))
    title(sprintf('Family %d', myfam))
    dev.off()
}
