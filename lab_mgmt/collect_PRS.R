# Collects the polygenic risk scores from PROFILE files, created by PRSice
suffix = 'noFlip_MAFbtp01_rsbtp5'
res_dir = sprintf('~/data/prs/geno2/imputation/%s/', suffix)

# read in result files
files = dir(path = res_dir, pattern = 'profile$')
prs = c()
for (f in files) {
  a = read.table(sprintf('%s/%s', res_dir, f), header=1)
  prs = cbind(prs, a$SCORE)
}
colnames(prs) = files

# cleaning weird looking NSB strings
clean_nsb = function(nsb) {
  if (grepl('@', nsb)) {
    nsb = strsplit(nsb, '@')[[1]][1]
    nsb = strsplit(nsb, '-')[[1]][3]
  }
  return(nsb)
}
nsbs = as.numeric(sapply(as.character(a$IID), clean_nsb))

# transform to a nice looking dataframe
prs_df = as.data.frame(cbind(nsbs, prs))
colnames(prs_df)[1] = 'NSB_GENOTYPE_INDEX'

# some NSBs have been genotyped twice. I checked a few of them and their PRS correlation is 
# > .99 between genotype waves, so let's just pick the first one
dups = duplicated(prs_df$NSB_GENOTYPE_INDEX)
prs_df = prs_df[!dups, ]

# merge NSB to MRNs
mrns = read.csv('~/data/baseline_prediction/prs/nsb_and_mrn.csv')

m = merge(mrns, prs_df, by.x='NSB', by.y='NSB_GENOTYPE_INDEX')

fname = sprintf('~/data/prs/PRS%s.csv', suffix)
write.csv(m, file=fname, row.names=F)
