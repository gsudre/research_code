families = read.table('~/philip/fam_pedigrees/fams.txt')
families = unique(families)
library(kinship2)
library(RColorBrewer)
palp = brewer.pal(9, "Reds")
paln = brewer.pal(9, "Blues")
# remove the whitest and reddest colors
palp = palp[2:8]
paln = rev(paln[2:8])  # make bluest the first one
ped = read.csv('~/philip/fam_pedigrees/pedigree.csv')
phe = read.csv('~/philip/fam_pedigrees/dti_mean_phenotype_cleanedWithinTract3sd_adhd_nodups_extendedAndNuclear_mvmt_pctMissingSE10_FAbt2.5.csv')
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
               # it's not affected (no color), need no value
               affected = append(affected, 0)
               vals = append(vals, NA)
          } else {
               affected = append(affected, 1)
               vals = append(vals, phe$fa_mean[as.character(phe$id) == id])
          }
          if (sum(as.character(dx$ID) == id) == 0) {
               sx = append(sx, 'Unknown')
          } else {
               idx = which(as.character(dx$ID) == id)
               sx = append(sx, as.character(dx$CURRENT_DX[idx]))
          }
     }
     zvals = scale(vals[!is.na(vals)])
     # let's fix the color scales now so we have positive and negative
     npos = length(zvals[zvals >= 0])
     nneg = length(zvals[zvals < 0])
     # expand the palette so that we have enough colors
     pcols <- colorRampPalette(palp)(npos)
     ncols <- colorRampPalette(paln)(nneg)
     cols = c(ncols, pcols)
     szvals = sort(zvals, index.return=T)
     ids = ped2$id[!is.na(vals)][szvals$ix]
     colors = vector()
     for (v in 1:length(vals)) {
          # if we find NA, it's either not in phenotype, or has a 0 as pheno
          if (is.na(vals[v])) {
               # and it was supposed to be filled in (true NA)
               if (affected[v]) {
                    # assign it the first color
                    colors = append(colors, cols[1])
               }
               # not affected NA doesn't matter (won't get colored anyways)
               else {
                    colors = append(colors, 'black')
               }
          # if we have a value, assign the appropriate color
          } else {
               cat(sprintf('\t%f\n', szvals$x[ids == ped2$id[v]]))
               mycol = cols[ids == ped2$id[v]][1]
               colors = append(colors, mycol)
          }
     }
     pdf(sprintf('~/philip/fam_pedigrees/zscore/withinFamily/fa_mean/%d.pdf', myfam))
     plot(ped2, col=colors, affected=affected, id=sx, cex=.7)
     title(sprintf('Family %d, phenotype z(FA_mean)', myfam))
     dev.off()
}

