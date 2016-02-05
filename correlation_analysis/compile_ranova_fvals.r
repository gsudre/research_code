path = '~/data/results/structural/perms/ranova/'
pattern = '^perm_repeatedMeasuresANOVA_subcortical_matchedDiffDSM4_perVSnv*'
files = list.files(path, pattern=pattern)
all_fvals = vector()
for (fname in files) {
	load(sprintf('%s/%s', path, fname))
	all_fvals = c(all_fvals, max_Fval)
}
ul = ceiling(.95*length(all_fvals))
cat('Fval:', sort(all_fvals)[ul])