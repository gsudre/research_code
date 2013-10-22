fname = "~/data/results/structural/repeatedMeasuresANOVA_Cortex_matchedDiffDSM4_perVSnv_%s.txt"

rft = 4.36 # threshold obtained using Random Field Theory
brain_data = c('dtL_thalamus_1473', 'dtR_thalamus_1473')
#                'dtL_striatum_1473', 'dtR_striatum_1473',
#                'dtL_cortex_SA_1473', 'dtR_cortex_SA_1473',
#                'dtL_gp', 'dtR_gp')
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
nverts = length(pvals)
Dim = c(sqrt(nverts),sqrt(nverts))
sFWHM = 5
resels = prod(Dim/c(sFWHM,sFWHM))
Z = seq(0,5,.01)
expEC = (resels*(4*log(2))*((2*pi)^(-3/2))*Z)*exp((Z^2)*(-0.5))
rft = Z[which(expEC<.05)[2]]
frft = min(fvals[pvals < 2*pnorm(-abs(rft))])
# adj_pvalsv = p.adjust(pvalsv, method='fdr')
cat('File: ', fname)
cat('\nMaximum F-val: ', max(fvals))
cat('\nGood uncorrected pvals:', sum(pvals<.05), '/', length(pvals))
cat('\nMinimum uncorrected F-val:', min(fvals[pvals<.05]))
cat('\nGood RFT pvals:', sum(fvals>frft), '/', length(fvals))
cat('\nMinimum RFT F-val:', frft, '(Z score:', rft, ')')
cat('\nGood FDR pvals:', sum(adj_pvals<.05), '/', length(adj_pvals))
cat('\nMinimum FDR F-val:', min(fvals[adj_pvals<.05]))
# cat('\nGood uncorrected pvals variance:', sum(pvalsv<.05), '/', length(pvalsv))
# cat('\nMinimum uncorrected F-val variance:', min(fvalsv[pvalsv<.05]))
# cat('\nGood corrected pvals variance:', sum(adj_pvalsv<.05), '/', length(adj_pvalsv))
# cat('\nMinimum corrected F-val variance:', min(fvalsv[adj_pvalsv<.05]))