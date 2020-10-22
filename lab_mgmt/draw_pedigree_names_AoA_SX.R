families = read.table('~/data/pedigrees/famids.txt')[,1]
families = unique(families)
library(kinship2)
library(RColorBrewer)
mycol = 2
pal = brewer.pal(9, "Reds")
# remove the whitest and reddest colors
pal = pal[2:8]
# expand the palette so that we have enough colors
ped = read.csv('~/data/pedigrees/pedigree_20201006.csv')
phe = read.csv('~/data/pedigrees/pheno.csv')
clin = read.csv('~/data/pedigrees/augmented_clinical_09272020.csv')
# don't use anything from PHilip's old files because it'd corrupt the initial
# age of assessment
clin = clin[clin$source!='PhilipsOldFiles',]
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
            # find sx info for individual
            sx_data = clin[as.character(clin$MRN)==id, ]
            # if we don't have sx data for this MRN
            if (nrow(sx_data) == 0) {
                max_inatt = NA
                max_hi = NA
                adult_inatt = NA
                adult_hi = NA
                age = NA
            } else {
                # check for childhood records
                ch_idx = as.character(sx_data$age_clin) == 'child'
                if (sum(ch_idx) > 0) {
                    max_inatt = max(sx_data[ch_idx, 'SX_inatt'])
                    max_hi = max(sx_data[ch_idx, 'SX_hi'])
                    sx_data = sx_data[!ch_idx, ]
                    # find age of first assessment
                    age_idx = which.min(as.numeric(sx_data$age_clin))
                    adult_inatt = sx_data[age_idx, 'SX_inatt']
                    adult_hi = sx_data[age_idx, 'SX_hi']
                    age = as.numeric(sx_data[age_idx, 'age_clin'])
                } else {
                    # for everyone who doesn't have a "child" from CAADID record
                    age_idx = which.min(as.numeric(sx_data$age_clin))
                    max_inatt = max(sx_data[age_idx, 'maxOverTimeSX_inatt'])
                    max_hi = max(sx_data[age_idx, 'maxOverTimeSX_hi'])
                    adult_inatt = NA
                    adult_hi = NA
                    age = as.numeric(sx_data[age_idx, 'age_clin'])
                }
            }
            sx_str = sprintf('%s\n%s\n(%.0f yo)\n%d : %d : %d : %d',
                             phe[idx,]$first.name, phe[idx,]$last.name, age,
                             max_inatt, max_hi, adult_inatt, adult_hi)
        } else {  # no phenotype for this id
            sx_str = sprintf('%s', id)
        }
        sx = c(sx, sx_str)  
    }
    pdf(sprintf('~/data/pedigrees/new_trees/%d.pdf', myfam))
    plot(ped2, symbolsize=1, id=sx, cex=.4, mar = c(4.1, 2.2, 4.1, 2.2))
    title(sprintf('Family %d', myfam))
    dev.off()
}
