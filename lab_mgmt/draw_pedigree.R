
families = read.table('~/tmp/fams.txt')
families = unique(families)
library(kinship2)
library(RColorBrewer)
mycol = 2
pal = brewer.pal(9, "Reds")
# remove the whitest and reddest colors
pal = pal[2:8]
# expand the palette so that we have enough colors
ped = read.csv('~/tmp/simplex.csv')
phe = read.csv('~/tmp/phen.csv')
for (f in 1:dim(families)[1]) {
     myfam = families[f, 1]
     cat(sprintf('Plotting family %d\n', myfam))
     idx = ped$FAMID==myfam
     ped2 = pedigree(ped[idx,]$ID, ped[idx,]$FA, ped[idx,]$MO, ped[idx,]$SEX, missid=0)
     affected = vector()
     vals = vector()
     sx = vector()
     for (id in ped2$id) {
          if (phe[as.character(phe$ID)==id,]$AFFECTED==0) {
               # affected = append(affected, 0)
               # vals = append(vals, NA)
               affected = append(affected, 0)
               vals = append(vals, 'black')
               sx = append(sx, '')
          } else {
               affected = append(affected, 1)
               # vals = append(vals, phe[as.character(phe$id)==id,mycol])
            #    if (phe[as.character(phe$id)==id, mycol] == 'ADHD') {
            #         vals = append(vals, pal[length(pal)])
            #    }
            #    else {
            #         vals = append(vals, pal[1])
            #    }
               vals = append(vals, 'black')
               sx_str = sprintf('%d', phe[as.character(phe$id)==id,]$id)
               sx = append(sx, '')
          }
     }
     svals = sort(vals, index.return=T)
     nscale = sum(!is.na(vals))
     cols <- colorRampPalette(pal)(nscale)
     colors = vector()
     for (v in vals) {
          if (is.na(v)) {
               colors = append(colors, 'black')
          } else {
               colors = append(colors, cols[svals$ix[svals$x==v]])
          }
     }
    #  pdf(sprintf('~/tmp/pedigrees/%d.pdf', myfam))
    #  plot(ped2, col=colors, affected=affected, symbolsize=.7)
     plot(ped2, col=vals, affected=affected, symbolsize=4, id=sx)
    #  title(sprintf('Family %d, phenotype %s', myfam, colnames(phe)[mycol]))
    #  dev.off()
}
