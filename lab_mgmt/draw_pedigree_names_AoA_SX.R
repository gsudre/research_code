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
clin = clin[as.character(clin$source)!='PhilipsOldFiles',]
for (myfam in families) {
    cat(sprintf('Plotting family %d\n', myfam))
    idx = ped$FAMID==myfam
    ped2 = pedigree(ped[idx,]$ID, ped[idx,]$FA, ped[idx,]$MO, ped[idx,]$SEX,
                    missid=0)
    affected = vector()
    vals = vector()
    sx = vector()
    adhd_count = 0  # adhd count per family
    nos_count = 0
    for (id in ped2$id) {
        imadhd = F
        imnos = F
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
                    age = as.numeric(sx_data[age_idx, 'age_clin'])
                    # sometimes adults don't have "child" records
                    if (age >= 17) {
                        adult_inatt = max(sx_data[age_idx, 'maxOverTimeSX_inatt'])
                        adult_hi = max(sx_data[age_idx, 'maxOverTimeSX_hi'])
                        max_inatt = NA
                        max_hi = NA
                    } else {
                        # kids
                        max_inatt = max(sx_data[age_idx, 'maxOverTimeSX_inatt'])
                        max_hi = max(sx_data[age_idx, 'maxOverTimeSX_hi'])
                        adult_inatt = NA
                        adult_hi = NA
                    }
                }
            }
            if (is.na(adult_inatt) && is.na(adult_hi)) {
                # don't need to print adult SX for kids
                sx_str = sprintf('%s\n%s\n(%.0f yo)\n%d : %d',
                             phe[idx,]$first.name, phe[idx,]$last.name, age,
                             max_inatt, max_hi)
                if (!is.na(max_inatt) && !is.na(max_hi)) {
                    if (max_inatt >= 6 || max_hi >= 6) {
                        imadhd = T
                        affected = c(affected, 1)
                    } else {
                        affected = c(affected, 0)
                    }
                    if (max_inatt >= 4 || max_hi >= 4) {
                        imnos = T
                    }
                } else {
                    affected = c(affected, NA)
                }
            } else {
                sx_str = sprintf('%s\n%s\n(%.0f yo)\n%d : %d\n%d : %d',
                                phe[idx,]$first.name, phe[idx,]$last.name, age,
                                max_inatt, max_hi, adult_inatt, adult_hi)
                # only go into ADHD decisions if we have some symptoms
                if (!is.na(adult_inatt) && !is.na(adult_hi)) {
                    if (adult_inatt >= 5 || adult_hi >= 5 ||
                        (!is.na(max_inatt) && max_inatt >= 6) ||
                        (!is.na(max_hi) && max_hi >= 6)) {
                        imadhd = T
                        affected = c(affected, 1)
                    } else {
                        affected = c(affected, 0)
                    }
                    if (adult_inatt >= 3 || adult_hi >= 3 ||
                        (!is.na(max_inatt) && max_inatt >= 4) ||
                        (!is.na(max_hi) && max_hi >= 4)) {
                        imnos = T
                    }
                } else {
                    affected = c(affected, NA)
                }
            }
        } else {  # no phenotype for this id
            sx_str = sprintf('%s', id)
            affected = c(affected, NA)
        }
        sx = c(sx, sx_str)
        adhd_count = adhd_count + imadhd
        nos_count = nos_count + imnos
    }
    pdf(sprintf('~/data/pedigrees/new_trees/%d.pdf', myfam))
    plot(ped2, symbolsize=1, id=sx, cex=.4, mar = c(4.1, 2.2, 4.1, 2.2), affected=affected)
    title(sprintf('Family %d (%d, %d, %d)', myfam, adhd_count, nos_count,
                  sum(!is.na(affected))))
    dev.off()
}
