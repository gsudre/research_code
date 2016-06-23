families = read.table('~/philip/fam_pedigrees/fams.txt')
families = unique(families)
library(kinship2)
library(RColorBrewer)
mycol = 2
pal = brewer.pal(9, "Reds")
# remove the whitest and reddest colors
pal = pal[2:8]
ped = read.csv('~/philip/fam_pedigrees/pedigree.csv')
phe = read.csv('~/philip/fam_pedigrees/demographics.csv')
dx = read.csv('~/philip/fam_pedigrees/dx_data_updated_philip.csv')
for (f in 1:dim(families)[1]) {
     myfam = families[f, 1]
     cat(sprintf('Plotting family %d\n', myfam))
     idx = ped$Famid==myfam
     ped2 = pedigree(ped[idx,]$ID, ped[idx,]$FA, ped[idx,]$MO, ped[idx,]$sex, missid=0)
     affected = vector()
     vals = vector()
     sx = vector()
     # for each ID in the pedigree
     for (id in ped2$id) {
          # if we don't find it in the phenotype file
          if (sum(as.character(phe$id)==id)==0) {
               # it's not affected (no color), need no value nor string ID
               affected = append(affected, 0)
               vals = append(vals, NA)
          } else {
               # we found ID in the phenotype, so it's a filled in shape
               affected = append(affected, 1)
               # the color is whatever value in mycol
               vals = append(vals, phe[as.character(phe$id)==id,mycol])

               # # it's only a filled in shape if we have a 1 in the column
               # if (phe[as.character(phe$id)==id, mycol] == 0) {
               #      affected = append(affected, 0)
               #      vals = append(vals, NA)
               # } else {
               #      affected = append(affected, 1)
               #      vals = append(vals, 1)
               # }

               # create a string to serve as identifier below the shape
               # sx_str = sprintf('%d + %d', phe[as.character(phe$id)==id,]$inatt, phe[as.character(phe$id)==id,]$hi)
               # sx = append(sx, sx_str)
          }
          if (sum(as.character(dx$ID) == id) == 0) {
               sx = append(sx, 'Unknown')
          } else {
               idx = which(as.character(dx$ID) == id)
               sx = append(sx, as.character(dx$CURRENT_DX[idx]))
          }
     }
     svals = sort(vals, index.return=T)
     nscale = sum(!is.na(vals))
     # expand the palette so that we have enough colors
     cols <- colorRampPalette(pal)(nscale)
     colors = vector()
     # for (v in 1:length(vals)) {
     #      # if we find NA, it's either not in phenotype, or has a 0 as pheno
     #      if (is.na(vals[v])) {
     #           # and it was supposed to be filled in
     #           if (affected[v]) {
     #                # we don't have a value for it, so assign it the first color
     #                colors = append(colors, cols[1])
     #           }
     #           # not affected NA is black
     #           else {
     #                colors = append(colors, 'black')
     #           }
     #      # if we have a value, assign the appropriate color
     #      } else {
     #           # colors = append(colors, cols[svals$ix[svals$x==vals[v]]])
     #           colors = append(colors, 'black')
     #      }
     # }

     # the colors don't matter in the binary phenotype, only whether it's
     # affected or not
     for (v in 1:length(vals)) {
          colors = append(colors, 'black')
     }
     pdf(sprintf('~/philip/fam_pedigrees/adhd/fmriORdti/%d.pdf', myfam))
     # sx = rep('', length(vals))
     # plot(ped2, col=colors, affected=affected)
     plot(ped2, col=colors, affected=affected, id=sx, cex=.7)
     # title(sprintf('Family %d, phenotype %s', myfam, colnames(phe)[mycol]))
     title(sprintf('Family %d, phenotype fMRI || DTI', myfam))
     dev.off()
}
