families = read.table('~/tmp/fams.txt')[,1]
families = unique(families)
library(kinship2)
library(RColorBrewer)
mycol = 2
pal = brewer.pal(9, "Reds")
# remove the whitest and reddest colors
pal = pal[2:8]
# expand the palette so that we have enough colors
ped = read.csv('/Volumes/Shaw/pedigrees/master/pedigree_20191216.csv')
phe = read.csv('~/tmp/pheno.csv')
for (myfam in families) {
    cat(sprintf('Plotting family %d\n', myfam))
    idx = ped$FAMID==myfam
    ped2 = pedigree(ped[idx,]$ID, ped[idx,]$FA, ped[idx,]$MO, ped[idx,]$SEX,
                    missid=0)
    affected = vector()
    vals = vector()
    sx = vector()
    for (id in ped2$id) {
        idx = as.character(phe$Medical.Record...MRN)==id
        # if we found phenotype for this ID
        if (sum(idx) > 0) {
            sx_str = sprintf('%s\n%s\n(%s)\n%.0f yo', phe[idx,]$First.Name,
                             phe[idx,]$Last.Name, id, phe[idx,]$age_at_consent)
        }
        else {
            sx_str = sprintf('%s', id)
        }
        sx = c(sx, sx_str)  
    }
    pdf(sprintf('~/tmp/pedigrees/%d.pdf', myfam))
    plot(ped2, symbolsize=1, id=sx, cex=.6, mar = c(4.1, 2.2, 4.1, 2.2))
    title(sprintf('Family %d', myfam))
    dev.off()
}
