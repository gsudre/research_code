
families = read.table('~/tmp/fams.txt')
families = unique(families)
library(kinship2)
library(RColorBrewer)
mycol = 4
pal = brewer.pal(9, "Reds")
# remove the whitest and reddest colors
pal = pal[2:8]
# expand the palette so that we have enough colors
ped = read.csv('~/data/solar_paper_v2/pedigree.csv')
phe = read.csv('~/tmp/tmp.csv')
for (f in 1:dim(families)[1]) {
     myfam = families[f, 1]
     cat(sprintf('Plotting family %d\n', myfam))
     idx = ped$Famid==myfam
     ped2 = pedigree(ped[idx,]$ID, ped[idx,]$FA, ped[idx,]$MO, ped[idx,]$sex, missid=0)
     affected = vector()
     vals = vector()
     sx = vector()
     for (id in ped2$id) {
          if (sum(as.character(phe$id)==id)==0) {
               affected = append(affected, 0)
               vals = append(vals, NA)
               sx = append(sx, '')
          } else {
               affected = append(affected, 1)
               vals = append(vals, phe[as.character(phe$id)==id,mycol])
               sx_str = sprintf('%d + %d', phe[as.character(phe$id)==id,]$inatt, phe[as.character(phe$id)==id,]$hi)
               sx = append(sx, sx_str)
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
     pdf(sprintf('~/Documents/colorful_pedigrees/%d.pdf', myfam))
     plot(ped2, col=colors, affected=affected)
     title(sprintf('Family %d, phenotype %s', myfam, colnames(phe)[mycol]))
     dev.off()
}
