fname = "~/data/results/structural/repeatedMeasuresANOVA_subcortical_matchedDiffDSM5_perVSNV_%s.txt"
brain_data = c('dtL_thalamus_1473', 'dtR_thalamus_1473', 
               'dtL_striatum_1473', 'dtR_striatum_1473',
#                'dtL_cortex_SA_1473', 'dtR_cortex_SA_1473',
               'dtL_gp', 'dtR_gp')
a = read.table(
    sprintf(fname, brain_data[1]),
    skip=3)
pvals = a[,2]
fvals = a[,1]
# # pvalsv = a[,4]
# fvalsv = a[,3]
for (b in 2:length(brain_data)) {
    a = read.table(
        sprintf(fname, brain_data[b]),
        skip=3)
    pvals = c(pvals, a[,2])
    fvals = c(fvals, a[,1])
#     pvalsv = c(pvalsv, a[,4])
#     fvalsv = c(fvalsv, a[,3])
}
adj_pvals = p.adjust(pvals, method='fdr')
# adj_pvalsv = p.adjust(pvalsv, method='fdr')
cat('Good uncorrected pvals:', sum(pvals<.05), '/', length(pvals))
cat('\nMinimum uncorrected F-val:', min(fvals[pvals<.05]))
cat('\nGood corrected pvals:', sum(adj_pvals<.05), '/', length(adj_pvals))
cat('\nMinimum corrected F-val:', min(fvals[adj_pvals<.05]))
# cat('\nGood uncorrected pvals variance:', sum(pvalsv<.05), '/', length(pvalsv))
# cat('\nMinimum uncorrected F-val variance:', min(fvalsv[pvalsv<.05]))
# cat('\nGood corrected pvals variance:', sum(adj_pvalsv<.05), '/', length(adj_pvalsv))
# cat('\nMinimum corrected F-val variance:', min(fvalsv[adj_pvalsv<.05]))